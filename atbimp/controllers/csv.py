import os
from cement import Controller, ex
from .components.cvsreader import CsvReader



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
   
   # Report Dict
   chkreport = {
      "fileChecked":       "",      # The file we are checking
      "linesRead":         0,       # Total number of lines in the file
      "dataLinesFound":    0,       # Total number of data lines found
      "incorrectDate":     0,       # Total number of lines with incorrect date
      "leadingQuote":      0,       # Total number of lines with a leading quote
      "trailingComma":     0,       # Total number of lines with a trailing comma 
      "recordsImported":   0,       # Total number of records imported.
   }

  
   ## ===============================================
   ## Controll er Code

   # import: import is a keyword that cannot be used as a method name  
   #
   @ex(help='import transactions from an ATB csv file',aliases=['import']) 
   def imp(self):
      '''
      imp | import <csv_file>    import and check csv_file into the import table of the
                                 transactions.db3 database.  The current contents of the 
                                 import table will be zapped.

      '''
      pass

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
      if not len(dTok[0]) == 2 and len(dTok[1]) == 2 and len(dTok[2]) == 4:
         newDate = "%s/%s/%s" % (('00'+dTok[0])[-2:], ('00'+dTok[1])[-2:], dTok[2])
         self.app.log.warning('  - line(%d):\tIncorrect date format: %s => %s' % (self.chkreport["linesRead"
         ], row[0], newDate))
         self.chkreport["incorrectDate"]+=1
         row[0] = newDate


      # Customer Ref Number `row[4]' sometimes has a leading "`" without
      # a closing one.  check and fix
      #
      if len(row[4]) and row[4][0] == "'":
         self.app.log.warning('  - line(%d):\tCust Ref field has leading (\'): %s => %s' % (self.chkreport["linesRead"
         ], row[4], row[4][1:]))
         self.chkreport["leadingQuote"]+=1
         row[4] = row[4][1:]

      # Some rows have a trailing comma giving it 11 cols instead of 10
      # check and fix
      if len(row) == 11:
         self.app.log.warning('  - line(%d):\tWrong number of cols, trailing (,): Truncating' % self.chkreport["linesRead"
         ])
         self.chkreport["trailingComma"]+=1
         row.pop()



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
      csv_file = self.app.pargs.csv_file
      db_tbl_cols = self.app.config.get('atbimp', 'db_tbl_cols')

      self.app.log.info("Checking csv file: %s" % csv_file)
      self.chkreport["fileChecked"] = csv_file

      # See if file exists and we can open this
      reader = CsvReader()
      if not reader.open(csv_file):
         self.app.log.error('Error reading from csv file: %s' % csv_file)
         return None
          

      row = reader.readline(); self.chkreport["linesRead"]+=1
      if reader.isHeaderLine(row):
         self.app.log.warning('  - Skipping header line: (1)%s....' % row[0])
         # Get another one
         row = reader.readline(); self.chkreport["linesRead"]+=1

      while not row is None:
         self._check_row(row) ; self.chkreport["dataLinesFound"]+=1
         row = reader.readline(); self.chkreport["linesRead"]+=1

      # Last line doesn't count
      self.chkreport["linesRead"]-=1

      # Looks like we're all done.  Let's print the results.
      #
      print(self.chkreport)

   # mrg: merge
   # 
   @ex(help='merge last imported file into transactions table', aliases=['merge'])
   def mrg(self):
      '''
      mrg | merge                merge the previously imported csv_file into table
                                 'import' with the transactions table.
      '''
      pass
