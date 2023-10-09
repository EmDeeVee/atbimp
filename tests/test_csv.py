import os
from atbimp.controllers.components.csv import CsvReader, CsvWriter
from pytest import raises
'''
csv tests.   Tests for the csv controller component designed to
work with the cement framework. 
'''

# ===============================================================
# Helper Functions
# ===============================================================
readFile =  './tests/test_in.csv'
writeFile = './tests/test_out.csv'

def create_readfile():
    # Create A read file to work with.

    # first check to see if there was a leftover
    # from a failed test.
    if os.path.exists(readFile):
        os.remove(readFile)

    # Create an empty file
    fh = os.open(readFile,os.O_RDWR | os.O_CREAT, 0o644)

    # And close here back up
    os.close(fh)

    return os.path.exists(readFile)


def write_csv_header():
    # Write a header to our file
    header="first name,last name,email\n"
    if os.path.exists(readFile): 
        fh = os.open(readFile, os.O_RDWR)
        os.write(fh, header.encode())
        os.close(fh)

        return True
    
    return False




def write_csv_data():
    # Write some bogus records to our file
    data = [
        'Kermit,"The Frog",kermit@muppets.local\n',
        'Miss,Piggy,misspiggy@muppets.local\n',
        'Fuzzy,Bear,fuzzybear@muppets.local\n'
    ]
    if os.path.exists(readFile):
        fh = os.open(readFile, os.O_RDWR)
        for row in data:
            os.write(fh, row.encode())
        os.close(fh)

        return True
    
    return False

    
# ===============================================================
# test Functions
# ===============================================================

def test_csv_create_reader():
    # Can we create a reader object
    reader = CsvReader()
    assert type(reader) == CsvReader


def test_csv_reader_open_file():
    # Can we open an existing file
    reader = CsvReader()
    ret = False

    if create_readfile():           # Make one
        if reader.open(readFile):   # Open it
            ret = True

    assert ret

def test_csv_reader_read_line():
    # Can we read a line from our file
    row=[]
    if create_readfile() and write_csv_data(): 
        reader = CsvReader()
        reader.open(readFile)
        row = reader.readline()

    assert len(row) > 0

def test_csv_reader_read_all_lines():
    # Can we read all the lines from our file
    nLinesRead = 0
    if create_readfile() and write_csv_data():
        reader = CsvReader()
        reader.open(readFile)
        row = reader.readline()
        while not row == None:
            nLinesRead+=1
            row = reader.readline()

    assert nLinesRead != 0

          


def test_csv_create_writer():
    # Can we create a writer object
    writer = CsvWriter()
    assert type(writer) == CsvWriter


