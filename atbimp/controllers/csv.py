import os
from cement import Controller, ex
from .components.cvsreader import CsvReader



@ex(help='Work with ATB csv files')
class Csv(Controller):
   class Meta:
      label = 'csv'
      help = """Commands for working ATB csv files. After a (sanity)check the
               requested csv file is imported into the temp table imports. Once
               you isue the 'csv merge' command the contents of the imports table
               will be merged into the transactions table
               """
      stacked_type = 'nested'
      stacked_on = 'base'
   
  
   ## ===============================================
   ## Controll er Code

   # import is a keyword that cannot be used as a method name  
   @ex(help='import transactions from an ATB csv file',aliases=['import']) 
   def imp(self):
      pass

   @ex(hide=True)
   def _check_row(self, row, rowNum):

      # print(row)
      # Date `row[0]' has inconconsistend date format
      # check and fix
      #
      dTok = row[0].split('/')
      if not len(dTok[0]) == 2 and len(dTok[1]) == 2 and len(dTok[2]) == 4:
         newDate = "%s/%s/%s" % (('00'+dTok[0])[-2:], ('00'+dTok[1])[-2:], dTok[2])
         self.app.log.warning('  - row(%d):\tIncorrect date format. Correcting %s => %s' % (rowNum, row[0], newDate))
         row[0] = newDate


      # Customer Ref Number `row[4]' sometimes has a leading "`" without
      # a closing one.  check and fix
      #
      if len(row[4]) and row[4][0] == "'":
         self.app.log.warning('  - row(%d):\tCust Ref field has leading quote(\'). Correcting %s => %s' % (rowNum, row[4], row[4][1:]))
         row[4] = row[4][1:]




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
      csv_file = self.app.pargs.csv_file
      self.app.log.info("Checking csv file: %s" % csv_file)

      # See if file exists and we can open this
      reader = CsvReader()
      if not reader.open(csv_file):
         self.app.log.error('Error reading from csv file: %s' % csv_file)
         return None
          

      row = reader.readline()
      if reader.isHeaderLine(row):
         self.app.log.warning('  - Skipping header line: (1)%s....' % row[0])
         # Get another one
         row = reader.readline()

      while not row is None:
         self._check_row(row, reader.nCurrentRow)
         row = reader.readline()


   @ex(help='merge last imported file into transactions table', aliases=['merge'])
   def mrg(self):
      pass
