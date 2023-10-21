import os
from atbimp.controllers.components.csv import CsvReader, CsvWriter
from pytest import raises
'''
csv tests.   Tests for the csv controller component designed to
work with the cement framework. 
'''

# ===============================================================
# Helper Functions and defenitions
# ===============================================================
readFile =  './tests/test_in.csv'
writeFile = './tests/test_out.csv'
tDataHeader = 'First name,Last Name, email'
tDataLine = ('id','Kermit','The Frog','kermit@muppets.local')
lDataLine = ['id','Kermit','The Frog','kermit@muppets.local']

def create_readfile():
    # Create A read file to work with.

    # first check to see if there was a leftover
    # from a failed test.
    if os.path.exists(readFile):
        os.remove(readFile)

    # Create an empty file
    fd = open(readFile, 'x')

    return os.path.exists(readFile)

def create_writefile():
    # Create A read file to work with.

    # first check to see if there was a leftover
    # from a failed test.
    if os.path.exists(writeFile):
        os.remove(writeFile)

    # Create an empty file
    fd = open(writeFile,'x')

    # and close it again
    fd.close()

    return os.path.exists(writeFile)


def write_csv_header():
    # Write a header to our file
    header="id,first name,last name,email\n"
    if os.path.exists(readFile): 
        with open(readFile, 'a') as file:
            file.write(header)

        return True
    
    return False

def write_csv_oneliner():
    if os.path.exists(readFile):
        with open(readFile, 'a') as file:
            file.write('1,Kermit,"The Frog",kermit@muppets.local\n')

        return True

    return False

def write_csv_data():
    # Write some bogus records to our file``
    data = [
        '1,Kermit,"The Frog",kermit@muppets.local\n',
        '2,Miss,Piggy,misspiggy@muppets.local\n',
        '3,Fuzzy,Bear,fuzzybear@muppets.local\n'
    ]
    if os.path.exists(readFile):
        with open(readFile, 'a') as file:
            for row in data:
                file.write(row)

        return True
    
    return False

    
# ===============================================================
# test Functions
# ===============================================================

# -------------------------------------------------------------
# Reader
#
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
    if create_readfile() and write_csv_oneliner(): 
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

def test_csv_reader_has_no_header():
    # Test to see if we regocnize that our file has no header
    if create_readfile() and write_csv_data():
        reader = CsvReader()
        reader.open(readFile)
        assert reader.hasHeader == False
    else:
        raise ConnectionError
    
def test_csv_reader_has_header():
    # Test to see if we regocnize that our file has no header
    if create_readfile() and write_csv_header() and write_csv_data():
        reader = CsvReader()
        reader.open(readFile)
        assert reader.hasHeader == True
    else:
        raise ConnectionError
    

# -------------------------------------------------------------
# Writer
#
def test_csv_create_writer():
    # Can we create a writer object
    writer = CsvWriter()
    assert type(writer) == CsvWriter

def test_csv_writer_write_row_as_list():
    # Can we write a line of data as a string
    res = 0             # Number of bytes written
    if create_writefile():
        writer = CsvWriter()
        if writer.open(writeFile):
            res = writer.writeline(lDataLine)

    assert res>0

def test_csv_writer_write_row_as_tuple():
    # Can we write a line of data as a string
    res = 0             # Number of bytes written
    if create_writefile():
        writer = CsvWriter()
        if writer.open(writeFile):
            res = writer.writeline(tDataLine)

    assert res>0




# -------------------------------------------------------------
# Cleanup
#
def test_csv_cleanup():
    # Cleanup.  Should be the last test in our series
    # asserts always True
    #
    if os.path.exists(readFile):
        os.remove(readFile)

    if os.path.exists(writeFile):
        os.remove(writeFile)
    
    assert True
