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
        self.reader = None                   # Hold the csv reader object
        self.fd_reader = None                # file handle for the reader
        self.hasHeader = False               # Does oru file have a header
    
    # Open the csv file
    def open(self,csvfile, snif=True):
        if not os.path.exists(csvfile):
            return False
        
        try:
            self.fd_reader = open(csvfile)

            # First we do a bit of sniffing
            sniffer = csv.Sniffer()
            sample = self.fd_reader.read(1024)
            self.fd_reader.seek(0);              # Reset file pointer
            if len(sample) > 10 and snif:        # Can't do anything with less bytes
                dialect = sniffer.sniff(sample, delimiters=',')
                self.hasHeader = sniffer.has_header(sample)
                self.reader = csv.reader(self.fd_reader, dialect)
            else:
                self.reader = csv.reader(self.fd_reader)
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
        
    # Pick up your mess before you leave.
    def __del__(self):
        if not self.fd_reader is None:
            self.fd_reader.close()


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
        # if not os.path.exists(csvfile):
        #     return False
        
        try:
            self.fd_writer = open(csvfile, "w")
            self.writer = csv.writer(self.fd_writer,dialect='excel', quoting=csv.QUOTE_NONNUMERIC)   
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
        if not self.fd_writer is None:
            self.fd_writer.close()
