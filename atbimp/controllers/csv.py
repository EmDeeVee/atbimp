import os
import re
from cement import Controller, ex
from .components.csv import CsvReader, CsvWriter



@ex(help='Work with ATB csv files')
class Csv(Controller):
    '''
    Class Csv(Controler): controller to handle the CSV portion of the AtbImportApp
    accesed by: atbimp csv <command>

    parameters: None
    '''
    class Meta:
        label = 'csv'
        help = "Commands for checking, importing and fixing ATB csv files."
        stacked_type = 'nested'
        stacked_on = 'base'
    
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        # Report Dict
        self.chkreport = {
            "fileChecked":       "",      # The file we are checking
            "fileExported":      "n/a",   # The file the export was written to
            "linesRead":         0,       # Total number of lines in the file
            "dataLinesFound":    0,       # Total number of data lines found
            "incorrectDate":     0,       # Total number of lines with incorrect date
            "leadingQuote":      0,       # Total number of lines with a leading quote
            "trailingComma":     0,       # Total number of lines with a trailing comma 
            "singleQuote":       0,       # Total number of lines containing a single quote in text
            "totalErrors":       0,       # Total number of errors found
            "recordsImported":   0,       # Total number of records imported.
            "recordsExported":   0,       # Total number of records exported.
            "sqlInsertErrors":   0,       # Total number of Sql Insert Errorrs.
            "duplicatesFound":   0,       # Total number of duplicates found.
        }
        # date format order used in this file.  We will regocnize the following formats.
        #   YYYY-MM-DD:     dateOrder will be [1,2,3]   # The format we want.
        #   m/d/YYYY:       dateOrder will be [3,1,2]   # will be prefixed with 0
        #   d/m/YYYY:       dateOrder will be [3,2,1]   # will be prefixed with 0
        #
        # Output format will always be YYYY-MM-DD
        #
        self.dateOrder = [1,2,3]    # Default no change.


    ## ====================================================================
    ## Helper Functions
    ##

    # ----------------------------------------------------------------------
    # _scan_date_format()
    # 
    # will read as many records as needed and available to figure out what
    # date format is used. Of both the day and month segment stay under 12
    # we will not be able to figure out the format.  In that case we will 
    # leave the date as it is.
    #
    #   TODO: Make this an argument so the user can force the date format.
    #
    @ex(hide=True)
    def _scan_date_format(self):
        # Keep reading rows until we know what date format we have in this one
        #
        max1 = 0
        max2 = 0
        rowsScanned = 0

        # Create the reader object
        csv_file = self.app.pargs.csv_file
        reader = self._createReader(csv_file)

        if reader:
            row = reader.readline();
            if self._isHeaderRow(row):
                # Get another one
                row = reader.readline()

            dTok=row[0].split('-')
            if len(dTok) == 3:
                # Asuming YYYY-MM-DD format.  We're done.  No further checks for now
                self.app.log.info('Date seems to be in correct format.  Using: YYYY-MM-DD')
                return rowsScanned+1

            dTok = row[0].split('/')
            if len(dTok) != 3:
                self.app.log.error('Cannot regognize date format.  Aborting date check')
                return rowsScanned+1
            
            # Go trough the motions
            while max1<=12 and max2<12 and row:
                max1 = max(max1,int(dTok[0]))
                max2 = max(max2,int(dTok[1]))
                rowsScanned+=1
                row = reader.readline();

            # Finished scanning or no more lines to check, let's see if we have
            # an outcome.
            #
            if max1<=12 and max2>12:
                self.dateOrder = [3,1,2]    # change m/d/Y -> Y-m-d
                self.app.log.info("Found date format in csv file: {m/d/Y}")
            elif max2<=12 and max1>12:
                self.dateOrder = [3,2,1]    # change d/m/Y  -> Y-m-d
                self.app.log.info("Found date format in csv file: {d/m/Y}")
            else:
                self.app.log.warning('Not enhough data to check format. found x/y/z format assuming m/d/y.')
                self.dateOrder = [3,1,2]
            
            return rowsScanned
        else:
            self.app.exit_code = self.app.EC_FILE_NOT_FOUND



    # ----------------------------------------------------------------------
    # _check_row:  Check the current row for known ATB csv errors
    #
    @ex(hide=True)
    def _check_row(self, row):
        '''
        _check_row(row, rowNum): Check and fix the current row for known ATB csv issues.
            1) date incorrect format: month and days<10 are sometimes
                not prefixed with a 0 and some files do m/d/y others do d/m/y
            2) Customer_Ref_Number (field:4) is sometimes preceded with a single (') without
                a closing quote.
            3) The header has 10 fields, where as some data lines have a trailing (,) thus
                generating 11 fields.
            4) The description (field:8) may contain single quotes.  Since none of the fields in the
                csv file are quoted, this is a trainwreck waiting to happen.  
        '''
        # ----------------------------------------------------------------------------------
        # Check 1: 
        #   Date `row[0]' has inconconsistend date format
        #   check and fix
        warn=""
        if self.dateOrder != [1,2,3]:
            # We have to convert d/m/Y or m/d/Y to YYYY-MM-DD
            dTok = row[0].split('/')
            warn = f"  - line({self.chkreport['linesRead']}):\tIncorrect date format: {row[0]} =>  "
            self.chkreport["incorrectDate"]+=1
            self.chkreport["totalErrors"]+=1
        else:
            # We should have y-m-d
            dTok = row[0].split('-')


        # Convert the date to the requested format and add a leading 0 
        # when needed.
        newDate = f"{dTok[self.dateOrder[0]-1]}-{dTok[self.dateOrder[1]-1]:0>2}-{dTok[self.dateOrder[2]-1]:0>2}"
        row[0] = newDate
        if len(warn):
            self.app.log.warning(f"{warn}{newDate}")



        # ----------------------------------------------------------------------------------
        # Check 2:
        #   Customer Ref Number `row[4]' sometimes has a leading "`" without
        #   a closing one.  check and fix
        #
        if len(row[4]) and row[4][0] == "'":
            self.app.log.warning(f'  - line({self.chkreport["linesRead"]}):\tCust Ref field has leading (\'): {row[4]} => {row[4][1:]}')
            self.chkreport["leadingQuote"]+=1
            self.chkreport["totalErrors"]+=1
            row[4] = row[4][1:]

        # ----------------------------------------------------------------------------------
        # Check 3:
        #   Description, field:8 may have single quotes in it.  Can't have that let's (single quotes see)
        #   so let's resplace them direct to sql quoting.  (aka: double-single-quotes)

        # simple fix
        if len(row[8].split("'")) != 1:
            data = "''".join([i for i in row[8].split("'") if i])

            # if new == old then there where no single quotes, only double-single-qoutes
            if len(data) != len(row[8]):
                self.app.log.warning(f'  - line({self.chkreport["linesRead"]}):\tSingle quotes found in description: Escaping')
                self.chkreport['singleQuote']+=1
                self.chkreport['totalErrors']+=1

            row[8] = data

        # ----------------------------------------------------------------------------------
        # Check 4:
        #   Some rows have a trailing comma giving it 11 cols instead of 10
        #   check and fix
        if len(row) == 11:
            self.app.log.warning(f'  - line({self.chkreport["linesRead"]}):\tWrong number of cols, trailing (,): Truncating')
            self.chkreport["trailingComma"]+=1
            self.chkreport["totalErrors"]+=1
            row.pop()


    # ----------------------------------------------------------------------
    # _isHeaderRow():  Check the current row for known ATB header
    #
    @ex(hide=True)
    def _isHeaderRow(self, row):
        '''
        _isHeaderRow(row)   Check to see of the row is a known ATB header.
                            ATB files don't use quoted strings therefore the 
                            csv.Sniffer() class cannot determine the header row.
        '''
        # No sniffer so we have to figure out if this is a header line
        # 
        # (Not a whole lot of checking here, for now)
        return row[0] == 'Transaction Date'

    # ----------------------------------------------------------------------
    # _createReader():  Check the current row for known ATB header
    #
    @ex(hide=True)
    def _createReader(self, csv_file, beSilent:bool = False):
        '''
        _createReader(csv_file)   Create a reader object and report this to user
        '''
        # See if file exists and we can open this
        if not beSilent:
            self.app.log.info(f"Checking and importing from csv file: {csv_file}")
            self.chkreport["fileChecked"] = csv_file
        reader = CsvReader()

        # Sniffer doesn't work on Atb Files, since it needs quoted values
        # to determine the delimiter
        #
        if not reader.open(csv_file, snif=False):
            self.app.log.error(f'Error reading from csv file: {csv_file}')
            return None

        return reader
    

    # ----------------------------------------------------------------------
    # _check_duplicate(): -> bool
    #
    # Check to see if this is a duplicate, if so import this into the 
    # duplicates table.
    #
    #  Return:  duplicate_of (transaction_id)
    #       0 : No duplicate was found
    #       >0: transaction_id of the record where this seemed to be a duplicate of
    #
    @ex(hide=True)
    def _check_duplicate(self, data):
        # Build a query to see if this transaction is already in the database.
        where = f"account_id = {data['account_id']} AND date ='{data['date']}' AND amount={data['amount']} AND dc='{data['dc']}' AND balance={data['balance']}"
        qry={
            'query':    'id',
            'from':     'transaction',
            'where':    where
        }
        res = self.app.sqlite3.select(qry)
        if len(res) != 0:
            # Houston, we have a duplicate
            # transaction_id = res[0]['id']

            # # Let's see if this is a first or not
            # res = self.app.sqlite3.select({'query': 'id', 'from': 'duplicate', 'where': f'transaction_id={transaction_id}'})
            # if len(res) == 0:
            #     # first time
            #     if not self.app.sqlite3.insert({'into': 'duplicate', 'data': {'transaction_id': transaction_id }}):
            #         raise ConnectionError
            #     duplicate_id = self.app.sqlite3._cur.lastrowid
            # else:
            #     # not a first
            #     duplicate_id = res[0]['id']

            # duplicate_entry has no account_id or month_id
            # del data['account_id']
            # del data['month_id']

            # but we do need a duplicate_id
            # data.update({'duplicate_id': duplicate_id})
            # if not self.app.sqlite3.insert({'into': 'duplicate_entry', 'data': data}):
            #     raise ConnectionError
            
            return res[0]['id']
            
        return 0
    
    
    # ----------------------------------------------------------------------
    # _import_transaction():  Import transaction into database
    #
    @ex(hide=True)
    def _import_transaction(self, row, importRowId):

        # Make a dict of our row
        dataIn = dict(zip(self.app.config.get(self.app.label,'exp_tbl_cols'),row))

        # First split data in a couple of sets

        # account
        dataAcct = dict(zip(
            list(self.app.sqlite3._models['account']['fields'].keys())[1:],
            (
                dataIn['account_number'][-4:],
                f"{int(dataIn['account_rtn']):09}",     # Convert to 9 digits with leading 0
                f"{int(dataIn['account_number']):012}"   # Convert to 12 digits with leading 0
            )
        ))

        # month
        dataMonth = dict(zip(
            list(self.app.sqlite3._models['month']['fields'].keys())[1:],
            (
                int(dataIn['date'][:4]),        # Year as an integer
                int(dataIn['date'][5:7])        # Month as an integer
            )
        ))

            

        # transaction

        # We don't want Debit and credit in a seperate cols
        amt = dataIn['debit_amount']; dc="D"
        if len(dataIn['credit_amount']):
            amt = dataIn['credit_amount']; dc="C"

        datTrans = dict(zip(
            # Skip id, account_id, month_id, import_id, import_line, flag and duplicate_of for now
            list(self.app.sqlite3._models['transaction']['fields'])[7:],  
            (
                dataIn['date'],
                dataIn['transaction_type'],
                dataIn['customer_ref_number'],
                amt,
                dc,
                dataIn['running_balance_amount'],
                dataIn['extended_text'],
                dataIn['bank_reference_number']
            )
        ))

        # Our data objects are almost ready
        # First the account table
        qry={'query': 'id, alias', 'from': 'account', 'where': f"alias LIKE '{dataAcct['alias']}'"}
        ret = self.app.sqlite3.select(qry)
        if not len(ret):
            # This account is not in the db yet. 
            self.app.sqlite3.insert({'into': 'account', 'data': dataAcct})

            # Try again
            ret = self.app.sqlite3.select(qry)
            if not len(ret): 
                # give up
                return False

        # Only interested in the first row answer of this query
        ret=ret[0]

        # We now have an id for our dataTrans object
        datTrans['account_id'] = ret['id']

        # Next we want to place the year-month in a different table to
        # speed up searches on complete month.
        qry={'query': '*', 'from': 'month', 'where': f"year={dataMonth['year']} and month={dataMonth['month']}"}
        ret = self.app.sqlite3.select(qry)
        if not len(ret):
            # This year-date combo is not yet in the database
            self.app.sqlite3.insert({'into': 'month', 'data': dataMonth})

            # Try again
            ret = self.app.sqlite3.select(qry)
            if not len(ret):
                # Give up
                return False
            
        # Only interested in the first row answer of this query
        ret=ret[0]

        # completing the datTrans object values
        datTrans['month_id'] = ret['id']
        datTrans['import_id'] = importRowId
        datTrans['import_line'] = self.chkreport['linesRead']

        # Before importing this row, check for duplicate.
        datTrans['flag'] = ' '
        datTrans['duplicate_of'] = self._check_duplicate(datTrans)
        if datTrans['duplicate_of']:
            datTrans['flag'] = 'D'
            self.chkreport['duplicatesFound'] += 1

        self.app.sqlite3.insert({'into': 'transaction', 'data': datTrans})            
        # if not self._check_duplicate(datTrans):
        #     # All good, lets import
        #     if self.app.sqlite3.insert({'into': 'transaction', 'data': datTrans}) == 1:
        #         return True
        # else:
        #     # not good, duplicate was inserted into duplicates table
        #     self.chkreport['duplicatesFound'] += 1
        #     self.chkreport['recordsImported'] -= 1  #  This one doesn't count

        # That's all there is to it.
        return True
            


    ## ====================================================================
    ## Controller Code
    ##

    # ----------------------------------------------------------------------
    # import: import is a keyword that cannot be used as a method name  
    #
    @ex(
            help='import transaction from an ATB csv file',
            label='import',
            aliases=['imp'],
            arguments=[(
                ['csv_file'],{
                    'help': 'csv file to import',
                    'action': 'store',
                }
            )]) 
    def ximport(self):
        '''
        imp | import <csv_file>     import and check csv_file into the transaction table of the
                                    database.  Any suspected duplicates will be stored in seperate
                                    tables for user review.

        '''
        # Scan our input file to see what date format we need to use.
        #
        self._scan_date_format()

        # Create the reader object
        csv_file = self.app.pargs.csv_file
        reader = self._createReader(csv_file)
            
        if reader:
            # Read the first line
            row = reader.readline(); self.chkreport["linesRead"]+=1
            if self._isHeaderRow(row): 
                self.app.log.warning(f'  - Skipping header line: (1){row[0]}....')
                # Get another one
                row = reader.readline(); self.chkreport["linesRead"]+=1

            # Log import action.
            importLog =  {
                'into': 'import',
                'data': {
                    'source': csv_file
                }
            }
            self.app.sqlite3.insert(importLog)
            impRowId = self.app.sqlite3._cur.lastrowid


            # Go trough the motions
            while not row is None:
                self._check_row(row) ; self.chkreport["dataLinesFound"]+=1
                if self._import_transaction(row, impRowId):
                    self.chkreport["recordsImported"]+=1
                else:
                    self.chkreport["sqlInsertErrors"]+=1

                row = reader.readline(); self.chkreport["linesRead"]+=1


            # Last line doesn't count
            self.chkreport["linesRead"]-=1

            # Looks like we're all done.  Let's print the results.
            #
            data = {}
            data["report"] = self.chkreport
            self.app.render(data, 'csv/report.jinja2')

        else:
            self.app.exit_code = self.app.EC_FILE_NOT_FOUND


    # ----------------------------------------------------------------------
    # chk: The check function as called from the command line
    #
    @ex(
            help='sanity check on import file',
            aliases=['chk'],
            arguments=[(
                ['csv_file'],{
                    'help': 'csv file to check',
                    'action': 'store',
                }
            )])
    def check(self):
        '''
        chk | check <csv_file>     check the csv file for know ATB csv issues.  
        '''
        # Scan our input file to see what date format we need to use.
        #
        self._scan_date_format()

        # Create the reader object
        csv_file = self.app.pargs.csv_file
        reader = self._createReader(csv_file)
        
        if reader:
            # Read the first line
            row = reader.readline(); self.chkreport["linesRead"]+=1
            if self._isHeaderRow(row): 
                self.app.log.warning(f'  - Skipping header line: (1){row[0]}....')
                # Get another one
                row = reader.readline(); self.chkreport["linesRead"]+=1

            while not row is None:
                self._check_row(row) ; self.chkreport["dataLinesFound"]+=1
                row = reader.readline(); self.chkreport["linesRead"]+=1

            # Last line doesn't count
            self.chkreport["linesRead"]-=1

            # Looks like we're all done.  Let's print the results.
            #
            data = {}
            data["report"] = self.chkreport
            self.app.render(data, 'csv/report.jinja2')
        else:
            self.app.exit_code = self.app.EC_FILE_NOT_FOUND

    # ----------------------------------------------------------------------
    # fix: 
    #
    @ex(
            help='read, check, fix and write back to a proper csv file',
            arguments=[
                (['csv_file'],{
                    'help': 'file to read data from',
                    'action': 'store'
                }),
                (['exp_file'],{
                    'help': 'file to export data to',
                    'action': 'store'
                })
            ]
        )
    def fix(self):
        '''
        fix  <csv_file> <exp_file>     check the csv file for know ATB csv issues.  
        '''
        # Scan our input file to see what date format we need to use.
        #
        self._scan_date_format()

        csv_file = self.app.pargs.csv_file
        exp_file = self.app.pargs.exp_file

        self.app.log.info(f"Checking csv file: {csv_file}")
        self.chkreport["fileChecked"] = csv_file

        # Create the reader object
        csv_file = self.app.pargs.csv_file
        reader = self._createReader(csv_file)

        if reader:

            # Create the writer.  No helper function yet since this code
            # is called only in export.
            #
            writer = CsvWriter()
            if not writer.open(exp_file):
                self.app.log.error(f'Error opening export file: {exp_file}')
                self.app.exit_code = self.app.EC_FILE_NOT_FOUND
                return
            self.chkreport["fileExported"] = exp_file
            
            # Read the first line
            row = reader.readline(); self.chkreport["linesRead"]+=1
            if self._isHeaderRow(row): 
                # are not processing the header row, however we do want it
                # in our output
                self.app.log.warning(f'  - Skipping header line: (1){row[0]}....')
                writer.writeline(row)

                # And, get another one
                row = reader.readline(); self.chkreport["linesRead"]+=1

            while not row is None:
                self._check_row(row) ; self.chkreport["dataLinesFound"]+=1
                writer.writeline(row); self.chkreport["recordsExported"]+=1

                # and get the net one
                row = reader.readline(); self.chkreport["linesRead"]+=1

            # Last line doesn't count
            self.chkreport["linesRead"]-=1

            # Looks like we're all done.  Let's print the results.
            #
            data = {}
            data["report"] = self.chkreport
            self.app.render(data, 'csv/report.jinja2')
        else:
            self.app.exit_code = self.app.EC_FILE_NOT_FOUND

