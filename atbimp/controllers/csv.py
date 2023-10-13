import os
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
        help = """Commands for working ATB csv files. After a (sanity)check the
                requested csv file is imported into the temp table imports. Once
                you isue the 'csv merge' command the contents of the imports table
                will be merged into the transactions table
                """
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
            "totalErrors":       0,       # Total number of errors found
            "recordsImported":   0,       # Total number of records imported.
            "recordsExported":   0,       # Total number of records imported.
        }

    
    ## ====================================================================
    ## Helper Functions
    ##

    # ----------------------------------------------------------------------
    # _check_row:  Check the current row for known ATB csv errors
    #
    @ex(hide=True)
    def _check_row(self, row):
        '''
        _check_row(row, rowNum): Check and fix the current row for known ATB csv issues.
            1) date incorrect format: months and days<10 are sometimes
                not prefixed with a 0
            2) Customer_Ref_Number (field:4) is sometimes preceded with a single (') without
                a closing quote.
            3) The header has 10 fields, where as some data lines have a trailing (,) thus
                generating 11 fields.
        '''

        # Date `row[0]' has inconconsistend date format
        # check and fix
        #
        dTok = row[0].split('/')
        if not (len(dTok[0]) == 2 and len(dTok[1]) == 2 and len(dTok[2]) == 4):
            newDate = "%s/%s/%s" % (('00'+dTok[0])[-2:], ('00'+dTok[1])[-2:], dTok[2])
            self.app.log.warning('  - line(%d):\tIncorrect date format: %s => %s' % (self.chkreport["linesRead"
            ], row[0], newDate))
            self.chkreport["incorrectDate"]+=1
            self.chkreport["totalErrors"]+=1
            row[0] = newDate


        # Customer Ref Number `row[4]' sometimes has a leading "`" without
        # a closing one.  check and fix
        #
        if len(row[4]) and row[4][0] == "'":
            self.app.log.warning('  - line(%d):\tCust Ref field has leading (\'): %s => %s' % (self.chkreport["linesRead"
            ], row[4], row[4][1:]))
            self.chkreport["leadingQuote"]+=1
            self.chkreport["totalErrors"]+=1
            row[4] = row[4][1:]

        # Some rows have a trailing comma giving it 11 cols instead of 10
        # check and fix
        if len(row) == 11:
            self.app.log.warning('  - line(%d):\tWrong number of cols, trailing (,): Truncating' % self.chkreport["linesRead"
            ])
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
    def _createReader(self, csv_file):
        '''
        _createReader(csv_file)   Create a reader object and report this to user
        '''
        # See if file exists and we can open this
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


    ## ====================================================================
    ## Controller Code
    ##

    # ----------------------------------------------------------------------
    # import: import is a keyword that cannot be used as a method name  
    #
    @ex(
            help='import transactions from an ATB csv file',
            aliases=['import'],
            arguments=[(
                ['csv_file'],{
                    'help': 'csv file to import',
                    'action': 'store',
                }
            )]) 
    def imp(self):
        '''
        imp | import <csv_file>    import and check csv_file into the import table of the
                                    transactions.db3 database.  The current contents of the 
                                    import table will be zapped.

        '''
        # Open the database
        self.app.sqlite3.set_dbfile(self.app.config.get('atbimp','db_file'))
        self.app.sqlite3.connect()
        modelAccounts = self.app.sqlite3.show_tables('accounts')
        if len(modelAccounts) == 0:
            self.app.sqlite3.create_table(self.app.config.get('atbimp','db_accounts_tbl'))
            # Try again
            modelAccounts = self.app.sqlite3.show_tables('accounts')
            if len(modelAccounts) == 0:
                # again?
                return

        # Create the reader object
        csv_file = self.app.pargs.csv_file
        reader = self._createReader(csv_file)
            
        # Read the first line
        row = reader.readline(); self.chkreport["linesRead"]+=1
        if self._isHeaderRow(row): 
            self.app.log.warning(f'  - Skipping header line: (1){row[0]}....')
            # Get another one
            row = reader.readline(); self.chkreport["linesRead"]+=1

        # Go trough the motions
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
        self.app.sqlite3.close()

    # ----------------------------------------------------------------------
    # chk: The check function as called from the command line
    #
    @ex(
            help='sanity check on import file',
            aliases=['check'],
            arguments=[(
                ['csv_file'],{
                    'help': 'csv file to check',
                    'action': 'store',
                }
            )])
    def chk(self):
        '''
        chk | check <csv_file>     check the csv file for know ATB csv issues.  
        '''
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
        csv_file = self.app.pargs.csv_file
        exp_file = self.app.pargs.exp_file
        # TODO: Not used.  Build an option to add default header 
        #       line when none exists.
        # exp_tbl_cols = self.app.config.get('atbimp', 'exp_tbl_cols')

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
                return self.app.EC_FILE_NOT_FOUND
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

