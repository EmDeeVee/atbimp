import csv
import os
from cement import Controller, ex



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
   
   """ CvsReader helper"""
   class CsvReader:
      reader=None          # Hold the csv reader object
      fh_reader=None       # file handle for the reader

      
      def open(self,csvfile):
         # if the file doesn't exist we're done
         if not os.path.exists(csvfile):
            return False
         
         try:
            self.fh_reader = open(csvfile)
            self.reader = csv.reader(self.fh_reader)
         except:
            return False
         
         return True
      
         
      def readline(self):
         try:
            row = self.reader.__next__()
            return row
         except:
            return False

      # Pick up your mess before you leave.
      def __del__(self):
         if not self.fh_reader is None:
            self.fh_reader.close()


   ## ===============================================
   ## Controll er Code

   # import is a keyword that cannot be used as a method name  
   @ex(help='import transactions from an ATB csv file',aliases=['import']) 
   def imp(self):
      pass

   @ex(hide=True)
   def _check_row(self, row):
      print(row)

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
      if not self.CsvReader.open(self, csv_file):
         self.app.log.error('Error reading from csv file: %s' % csv_file)
         return None
          
      
      row = self.CsvReader.readline(self)
      while not row is False:
         self._check_row(row)
         row = self.CsvReader.readline(self)


   @ex(help='merge last imported file into transactions table', aliases=['merge'])
   def mrg(self):
      pass
