import os
import pytest
from atbimp.main import AtbImpAppTest


def get_chkreport(app):
    '''
        chkreport = {
            "fileChecked":       "",      # The file we are checking
            "fileExported":      "n/a",   # The file the export was written to
            "linesRead":         0,       # Total number of lines in the file
            "dataLinesFound":    0,       # Total number of data lines found
            "incorrectDate":     0,       # Total number of lines with incorrect date
            "leadingQuote":      0,       # Total number of lines with a leading quote
            "trailingComma":     0,       # Total number of lines with a trailing comma 
            "recordsImported":   0,       # Total number of records imported.
            "recordsExported":   0,       # Total number of records imported.
    }
    '''
    return app.controller._controllers_map['csv'].chkreport

@pytest.fixture
def TestAppNoArg():
    with AtbImpAppTest() as app:        
        app.run()
        yield app

@pytest.fixture
def TestAppArgs(request):
    argv = request.node.get_closest_marker('argv').args[0]
    with AtbImpAppTest(argv=argv) as app:        
        app.run()
        yield app


def test_atbimp(TestAppNoArg):
    # test atbimp without any subcommands or arguments
    assert TestAppNoArg.exit_code == 0

@pytest.mark.argv(['--debug'])
def test_atbimp_debug(TestAppArgs):
    # test that debug mode is functional
    assert TestAppArgs.debug is True

@pytest.mark.argv(['--debug'])
def test_atbimp_ext_sqlite(TestAppArgs):
    # test that sqlite extension is functional
    dbfile = os.path.basename(TestAppArgs.sqlite3.get_dbfile())
    assert dbfile == 'mydatabase.db3'

@pytest.mark.argv(['csv'])
def test_atbimp_csv_no_args(TestAppArgs):
    # will just display help and exit code 0
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0
    assert report['linesRead'] == 0

def test_atbimp_csv_chk_no_args():
    # Will throw a System Exit (2) and complains about no files given
    argv=['csv', 'chk']
    with AtbImpAppTest(argv=argv) as app:
        with pytest.raises(SystemExit) as e_info:
            app.run()
            assert e_info.code == 2



@pytest.mark.argv(['csv', 'chk', './tests/nonexistent.csv'])
def test_atbimp_csv_chk_non_exis_file(TestAppArgs):
    # Argparser is satisfied, our controller will set exit code
    assert TestAppArgs.exit_code == TestAppArgs.EC_FILE_NOT_FOUND



#  ********* ******** ************ *********** **********
#  From here one we will use real .tcsv files for testing
#  so we can ignore real .csv files in .gitignore and make
#  these files part of the test setup.
#
@pytest.mark.argv(['csv', 'chk', './tests/no_errors_with_header.tcsv'])
def test_atbimp_csv_chck_no_errors_with_header(TestAppArgs):
    # Check a file that has no errors
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['totalErrors'] == 0

@pytest.mark.argv(['csv', 'chk', './tests/no_errors_no_header.tcsv'])        
def test_atbimp_csv_chck_no_errors_no_header(TestAppArgs):
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0  
    assert report['linesRead'] == 5 
    assert report['dataLinesFound'] == 5
    assert report['totalErrors'] == 0

@pytest.mark.argv(['csv', 'chk', './tests/trailing_comma.tcsv'])        
def test_atbimp_csv_chck_trailing_comma(TestAppArgs):
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['trailingComma'] == 3
    assert report['totalErrors'] == 3
        
@pytest.mark.argv(['csv', 'chk', './tests/wrong_date.tcsv'])
def test_atbimp_csv_chck_wrong_date(TestAppArgs):
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['incorrectDate'] == 4
    assert report['totalErrors'] == 4
        
@pytest.mark.argv(['csv', 'chk', './tests/leading_quote.tcsv'])        
def test_atbimp_csv_chck_leading_quote(TestAppArgs):
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['leadingQuote'] == 2
    assert report['totalErrors'] == 2

@pytest.mark.argv(['csv', 'chk', './tests/mixed_errors.tcsv'])      
def test_atbimp_csv_chck_mixed_errors(TestAppArgs):
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['incorrectDate'] == 3
    assert report['leadingQuote'] == 2
    assert report['trailingComma'] == 4
    assert report['totalErrors'] == 9
        
# 'fix' uses the same check routines as chk.  So no need for re-testing the
# checks with the provided input files. However, we are going to write an 
# output file here so that needs to be tested
#
def test_atbimp_csv_fix_no_args():
    # Will throw a System Exit (2) and complains about no files given
    argv = ['csv', 'fix']
    with AtbImpAppTest(argv=argv) as app:
        with pytest.raises(SystemExit) as e_info:
            app.run()
            assert e_info.code == 2

def test_atbimp_csv_fix_non_exist_in_file_no_out_file():
    # Will throw a System Exit (2) and complains about no files given
    argv = ['csv', 'fix', './tests/nonexistant.csv']
    with AtbImpAppTest(argv=argv) as app:
        with pytest.raises(SystemExit) as e_info:
            app.run()
            assert e_info.code == 2

@pytest.mark.argv(['csv', 'fix', './tests/nonexistant_in.csv', './tests/nonexistant_out.csv'])
def test_atbimp_csv_fix_non_exist_in_file_non_exist_out_file(TestAppArgs):
    # Argparser is satisfied, our controller will set exit code
    assert TestAppArgs.exit_code == TestAppArgs.EC_FILE_NOT_FOUND

@pytest.mark.argv(['csv', 'fix', './tests/mixed_errors.csv', './tests/nonexistant_out.csv'])
def test_atbimp_csv_fix_in_file_non_exist_out_file(TestAppArgs):
    # Argparser is satisfied, our controller will set exit code
    assert TestAppArgs.exit_code == TestAppArgs.EC_FILE_NOT_FOUND

@pytest.mark.argv(['csv', 'fix', './tests/mixed_errors.tcsv', './tests/fixed.tcsv'])
def test_atbimp_csv_fix_mixed_errors(TestAppArgs):
    # Argparser is satisfied, our controller will set exit code
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['incorrectDate'] == 3
    assert report['leadingQuote'] == 2
    assert report['trailingComma'] == 4
    assert report['totalErrors'] == 9

@pytest.mark.argv(['csv', 'chk', './tests/fixed.tcsv'])
def test_atbimp_csv_chk_fixed(TestAppArgs):
    # Re check the corrected file from the previous test
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['incorrectDate'] == 0
    assert report['leadingQuote'] == 0
    assert report['trailingComma'] == 0
    assert report['totalErrors'] == 0

    if os.path.exists('./tests/fixed.tcsv'):
        os.remove('./tests/fixed.tcsv')


def test_atbimp_csv_imp_no_args():
    # Will throw a System Exit (2) and complains about no files given
    argv = ['csv', 'imp']
    with AtbImpAppTest(argv=argv) as app:
        with pytest.raises(SystemExit) as e_info:
            app.run()
            assert e_info.code == 2

@pytest.mark.argv(['csv', 'imp', './tests/mixed_errors.tcsv'])
def test_atbimp_csv_imp_mixed(TestAppArgs):
    # Try importing our test file mixed.tcsv
    # FIXME: Need another test database file
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 

