import os
import sqlite3
import pytest
from atbimp.main import AtbImpAppTest


## ====================================================================
## Helper Functions
##
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

def create_tmpdb(inputFile):
    # a faulty test wil leave a db file behind. So let's get 
    # rid of it.
    destroy_tmpdb(inputFile)

    # now we can do the work
    dbFile = inputFile[:-4]
    con=sqlite3.connect(dbFile)
    cur=con.cursor()
    with open(inputFile) as inp:
        sql=inp.read()
        inp.close()

    cur.executescript(sql)
    con.commit()
    con.close()

    # override the db file
    os.environ['ATBIMP_DB_FILE'] = dbFile


def destroy_tmpdb(inputFile):
    dbfile=inputFile[:-4]
    if os.path.exists(dbfile):
        os.remove(dbfile)
    os.unsetenv('ATBIMP_DB_FILE')


## ====================================================================
## Fixtures
##
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

@pytest.fixture
def TestAppDb(request):
    argv = request.node.get_closest_marker('argv').args[0]
    with AtbImpAppTest(argv=argv) as app:
        app.run()
        yield app

        dbfile = app.sqlite3.dbfile()
        if os.path.exists(dbfile):
            os.remove(dbfile)

@pytest.fixture
def TestAppDb2Months(request):
    # A testapp that runs on twomonths.db3.  We have to pre-populate
    # this database with data, so we can use this as a fixture for our
    # tests.
    #
    create_tmpdb('./tests/twomonths.db3.sql')

    # Now we can setup our app
    #

    argv = request.node.get_closest_marker('argv').args[0]
    with AtbImpAppTest(argv=argv) as app:
        app.run()
        yield app

    destroy_tmpdb('./tests/twomonths.db3.sql')


# ====================================================================
# Tests
#
def test_atbimp(TestAppNoArg: AtbImpAppTest):
    # test atbimp without any subcommands or arguments
    assert TestAppNoArg.exit_code == 0

@pytest.mark.argv(['--debug'])
def test_atbimp_debug(TestAppArgs):
    # test that debug mode is functional
    assert TestAppArgs.debug is True

@pytest.mark.argv(['--debug'])
def test_atbimp_ext_sqlite(TestAppArgs):
    # test that sqlite extension is functional
    dbfile = os.path.basename(TestAppArgs.sqlite3.dbfile())
    assert dbfile == 'transactions.db3'

@pytest.mark.argv(['-db', './tests/twomonths.db3'])
def test_atbimp_ext_sqlite_db_file(TestAppArgs):
    # test that sqlite extension is functional
    dbfile = os.path.basename(TestAppArgs.sqlite3.dbfile())
    assert dbfile == 'twomonths.db3'
    
    # Still have to delete it once the test was successfull
    # we (ab)use destro_tmpdb() for this, even though we did
    # not create it with its peer create_tmpdb()
    destroy_tmpdb('./tests/twomonths.db3.sql')  # No, the `.sql' is not an typo

# --------------------------------------------------------------------
# Csv
#
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
    # Check a file that has no errors, except for all the data fields
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['totalErrors'] == 5

@pytest.mark.argv(['csv', 'chk', './tests/no_errors_no_header.tcsv'])        
def test_atbimp_csv_chck_no_errors_no_header(TestAppArgs):
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0  
    assert report['linesRead'] == 5 
    assert report['dataLinesFound'] == 5
    assert report['totalErrors'] == 5

@pytest.mark.argv(['csv', 'chk', './tests/trailing_comma.tcsv'])        
def test_atbimp_csv_chck_trailing_comma(TestAppArgs):
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['trailingComma'] == 3
    assert report['totalErrors'] == 8
        
@pytest.mark.argv(['csv', 'chk', './tests/wrong_date.tcsv'])
def test_atbimp_csv_chck_wrong_date(TestAppArgs):
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['incorrectDate'] == 5
    assert report['totalErrors'] == 5
        
@pytest.mark.argv(['csv', 'chk', './tests/leading_quote.tcsv'])        
def test_atbimp_csv_chck_leading_quote(TestAppArgs):
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 6
    assert report['dataLinesFound'] == 5
    assert report['leadingQuote'] == 2
    assert report['totalErrors'] == 7

@pytest.mark.argv(['csv', 'chk', './tests/mixed_errors.tcsv'])      
def test_atbimp_csv_chck_mixed_errors(TestAppArgs):
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 7
    assert report['dataLinesFound'] == 6
    assert report['incorrectDate'] == 6
    assert report['leadingQuote'] == 2
    assert report['trailingComma'] == 5
    assert report['totalErrors'] == 14
        
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
    assert report['linesRead'] == 7
    assert report['dataLinesFound'] == 6
    assert report['incorrectDate'] == 6
    assert report['leadingQuote'] == 2
    assert report['trailingComma'] == 5
    assert report['totalErrors'] == 14

@pytest.mark.argv(['csv', 'chk', './tests/fixed.tcsv'])
def test_atbimp_csv_chk_fixed(TestAppArgs):
    # Re check the corrected file from the previous test
    # FIXME: When a quote was found check if it is not already double-single-quoted
    report = get_chkreport(TestAppArgs)
    assert TestAppArgs.exit_code == 0 
    assert report['linesRead'] == 7
    assert report['dataLinesFound'] == 6
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
def test_atbimp_csv_imp_mixed(TestAppDb):
    # Try importing our test file mixed.tcsv
    # TODO: Need another test database file
    report = get_chkreport(TestAppDb)
    assert TestAppDb.exit_code == 0 
    assert report['linesRead'] == 7
    assert report['dataLinesFound'] == 6
    assert report['incorrectDate'] == 6
    assert report['leadingQuote'] == 2
    assert report['singleQuote'] == 1
    assert report['trailingComma'] == 5
    assert report['totalErrors'] == 14

@pytest.mark.argv(['csv', 'imp', './tests/duplicates_with_header.tcsv'])
def test_atbimp_csv_imp_duplicates(TestAppDb):
    # Try importing our test file mixed.tcsv
    # TODO: Need another test database file
    report = get_chkreport(TestAppDb)
    assert TestAppDb.exit_code == 0 
    assert report['linesRead'] == 9
    assert report['dataLinesFound'] == 8
    assert report['incorrectDate'] == 8
    assert report['duplicatesFound'] == 3
    assert report['recordsImported'] == 8
    assert report['totalErrors'] == 8


# --------------------------------------------------------------------
# Data
#
@pytest.mark.argv(['data', 'show'])
def test_atbimp_data_show(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0

@pytest.mark.argv(['data', 'show', '-m', 'January'])
def test_atbimp_data_show_faulty_month(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == TestAppDb2Months.EC_PARAM_WRONG_FORMAT

@pytest.mark.argv(['data', 'show', '-r', '2022/02/02:2022/02/27'])
def test_atbimp_data_show_faulty_range(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == TestAppDb2Months.EC_PARAM_WRONG_FORMAT

@pytest.mark.argv(['data', 'show', '-m', '2022-11', '-a', 'NoneExistingAccount'])
def test_atbimp_data_show_faulty_account(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == TestAppDb2Months.EC_PARAM_WRONG_FORMAT

@pytest.mark.argv(['data', 'show', '-m', '2022-11', '-a', '1234'])
def test_atbimp_data_show_month_one_account(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0

@pytest.mark.argv(['data', 'show', '-m', '2022-11', '-a', 'Unlimited'])
def test_atbimp_data_show_month_one_account_nickname(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0

@pytest.mark.argv(['data', 'show', '-m', '2022-11'])
def test_atbimp_data_show_month_all_accounts(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0

@pytest.mark.argv(['data', 'show', '-d', '2022-11-10'])
def test_atbimp_data_show_date_all_accounts(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0

@pytest.mark.argv(['data', 'show', '-d', '2022-11-10', '-a', 'Unlimited'])
def test_atbimp_data_show_date_one_account(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0

@pytest.mark.argv(['data', 'locate', '500.00'])
def test_atbimp_data_locate_amt(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0

@pytest.mark.argv(['data', 'locate', 'master'])
def test_atbimp_data_locate_desc(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0

@pytest.mark.argv(['data', 'locate', '500.00', '-a', '1234'])
def test_atbimp_data_locate_amt_acct(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0



# --------------------------------------------------------------------
# Imports
#
@pytest.mark.argv(['imports','list'])
def test_atbimp_imports_list(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0

@pytest.mark.argv(['imports','show', '3'])
def test_atbimp_imports_show_1(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0

# --------------------------------------------------------------------
# Accounts
#
@pytest.mark.argv(['accounts','list'])
def test_atbimp_accounts_list(TestAppDb2Months):
    assert TestAppDb2Months.exit_code == 0
    