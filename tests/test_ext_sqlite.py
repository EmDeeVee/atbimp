import os
from pytest import raises
from atbimp.main import AtbImpAppTest

# ===============================================================
# Helper Functions
# ===============================================================
testdb='./tests/test.db3'

def sqlite_connect(app):
    ''' Helper function: Opening the sqlite3 test connection '''

    # Check to see if there is still a left over test.db3 file 
    # from a failed test.  If so: Get rid of it.
    #
    if os.path.exists(testdb):
        os.remove(testdb)
    app.sqlite3.set_dbfile(testdb)
    app.sqlite3.connect()

def sqlite_cleanup(app):
    ''' Helper function: Close and/or cleanup sqlite3 test connection '''
    db_file = app.sqlite3.get_dbfile()
    app.sqlite3.close()
    os.remove(db_file)

def sqlite_create_test_model(ord=0):
    ''' Helper function: Create a test table dict'''
    if ord == 0:
        ord = ""
    model={
        'name':     f"test{ord}", 
        'fields':   [
            "'id' INTEGER",
            "'date' DATE",
            "'txt' TEXT",
            "'price' DECIMAL(10,2)"
        ]
    }
    return model


# ===============================================================
# Test Functions
# ===============================================================
def test_ext_sqlite():
    # test that sqlite extension is functional
    argv = ['--debug']
    with AtbImpAppTest(argv=argv) as app:
        app.run()
        app.sqlite3.set_dbfile(testdb)
        assert os.path.basename(app.sqlite3.get_dbfile()) == os.path.basename(testdb)

def test_ext_sqlite_connect():
    # test that sqlite is creating a database file and closes it
    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        assert os.path.exists(app.sqlite3.get_dbfile())
        sqlite_cleanup(app)

def test_ext_sqlite__get_table_info():
    # test that the _get_table_info works properly
    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        model = sqlite_create_test_model()
        res = app.sqlite3.create_table(model)

        # In assert we (for now) only check the name and the first field
        assert res['name'] == model['name']  and f"'{res['fields'][0]['name']}' {res['fields'][0]['type']}" == model['fields'][0]
        sqlite_cleanup(app)     # So assert will fail

def test_ext_sqlite_create_table():
    # test that sqlite is creating a test table
    # and we can read this back from the database
    #
    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        model = app.sqlite3.create_table(sqlite_create_test_model())
        assert model['name'] == 'test'
        sqlite_cleanup(app)

def test_ext_sqlite_show_tables_no_filter():
    # Test the show_tables() function with no filter

    # First create 3 test tables.  test1, test3, test3
    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        model1 = app.sqlite3.create_table(sqlite_create_test_model(1))
        model2 = app.sqlite3.create_table(sqlite_create_test_model(2))
        model3 = app.sqlite3.create_table(sqlite_create_test_model(3))
        
        ret = app.sqlite3.show_tables()
        assert ret[0]['name'] == 'test1' and ret[1]['name'] == 'test2' and ret[2]['name'] == 'test3'

def test_ext_sqlite_show_tables_test_filter():
    # Test the show_tables() function with no filter

    # First create 4 test tables.  test, test1, test3, test3
    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        model0 = app.sqlite3.create_table(sqlite_create_test_model())
        model1 = app.sqlite3.create_table(sqlite_create_test_model(1))
        model2 = app.sqlite3.create_table(sqlite_create_test_model(2))
        model3 = app.sqlite3.create_table(sqlite_create_test_model(3))
        
        # This shoudl only return 3 tables
        ret = app.sqlite3.show_tables('test_')
        assert len(ret) == 3 and ret[0]['name'] == 'test1' and ret[1]['name'] == 'test2' and ret[2]['name'] == 'test3'
