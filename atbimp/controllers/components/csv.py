import os
import csv

'''
    Using the csv library to handle read and writes and incapucalte them in helper
    classes CvsReader() and CvsWriter(). 

    Upon furter reading the documentation (RTFM) it looks like this class is 
    not even using half of the capebilities provided by lib/csv.

    TODO: update csv to better utilize lib/csv

'''

""" CsvReader helper"""
class CsvReader():
    '''
    class CsvReader():          Helper class for the class: Csv. Implements Lib/csv reader                            
    '''
    def __init__(self) -> None:
        self.reader=None                   # Hold the csv reader object
        self.fh_reader=None                # file handle for the reader

    # Check if this is a header line
    def isHeaderLine(self, row):
        if row[0] == 'Transaction Date':
            return True
        return 
    
    
    # Open the csv file
    def open(self,csvfile):
        if not os.path.exists(csvfile):
            return False
        
        try:
            self.fh_reader = open(csvfile)
            self.reader = csv.reader(self.fh_reader)
        except:
            return False
        
        return True
    
    
    # Read the next line
    def readline(self):
        try:
            row = self.reader.__next__()
            return row
        
        except:
            return None
        
    # Convert row to dict
    def row2dict(self, labels, row) -> dict:
        dct = {}
        try:
            for i,fld in enumerate(row):
                dct[labels[i]] = row[i]

        except:
            return None
        
        return dct

    # Pick up your mess before you leave.
    def __del__(self):
        if not self.fh_reader is None:
            self.fh_reader.close()


""" CsvWriter helper"""
class CsvWriter():
    '''
    class CsvWriter():          Helper class for the class: Csv. Implements Lib/csv writer                            
    '''
    def __init__(self) -> None:
        self.writer=None                   # Hold the csv writer object
        self.fd_writer=None                # file handle for the writer
    
    # Open the csv file
    def open(self,csvfile):
        if not os.path.exists(csvfile):
            return False
        
        try:
            self.fd_writer = open(csvfile, "w")
            self.writer = csv.writer(self.fd_writer)   
        except:
            return False
        
        return True
    
    
    def writeHeaderLine(self, hdr):
        # Simply write back the header that was found by the Reader
        pass

    # Write a line of data. 
    def writeline(self, data):        
        bytesWrittem = 0
        try:
            bytesWritten = self.writer.writerow(data)
        except:
            raise ConnectionError

        return bytesWritten


        
        
    # Pick up your mess before you leave.
    def __del__(self):
        if not self.fh_writer is None:
            self.fh_writer.close()
