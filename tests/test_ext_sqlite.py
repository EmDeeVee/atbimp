import os,random
import pytest
from atbimp.main import AtbImpAppTest
'''
ext_sqlite3 tests.   Tests for the sqlite3 extention designed to
work with the cement framework. 

    TODO: Separate the tests from the AtbImpApp. 
    Still need cement some how.  Since the extention requires
    an (app) to work with.  Therefore standalone unit testing
    would require further abstraction and with that kinda kills 
    the design decision to create an extension for cement.

    FIXME: Make tests confirm with pytest (like: test_atbimp.py)

'''

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
            "'id' INTEGER PRIMARY KEY AUTOINCREMENT",
            "'date' DATE",
            "'txt' TEXT",
            "'price' DECIMAL(10,2)"
        ]
    }
    return model

def sqlite_create_insert_dict(model, dataOption=False):
    ''' Helper fuction to create dict for insert statment '''
    ins = {
        'into': model,
    }
    fruits=('banana', 'apple', 'pear', 'raspbery', 'fig', 'pineapple')
    fruitIdx = random.randint(0,5)

    if dataOption:
        # use the data option
        ins['data'] = {
            'date': '#CURRENT_DATE',
            'txt':   fruits[fruitIdx],
            'price': int(random.random()*10000)/100
        }
    else:
        # Use cols/values pair
        ins['cols'] = ('date', 'txt', 'price')
        ins['values'] = ('#CURRENT_DATE', fruits[fruitIdx], int(random.random()*10000)/100)

    return ins

def sqlite_create_10_insert_for_select_clauses():
    ''' Create an insert statement with 10 Test rows for select clauses testing '''
    ret = '''INTO test(txt,price) VALUES
        ('test_1', 1.0),
        ('test_2', 2.0),
        ('test_3', 3.0),
        ('test_4', 0.0),
        ('test_5', 1.0),
        ('test_6', 2.0),
        ('test_7', 3.0),
        ('test_8', 0.0),
        ('test_9', 1.0),
        ('test_10', 2.0)
    '''
    return ret

# ===============================================================
# Test Functions
# ===============================================================
@pytest.fixture
def TestApp(request):
    argv = request.node.get_closest_marker('argv').args[0]
    with AtbImpAppTest(argv=argv) as app:        
        app.run()
        sqlite_connect(app)
        yield app
        sqlite_cleanup(app)

@pytest.mark.argv(['--debug'])
def test_ext_sqlite(TestApp):
    # test that sqlite extension is functional
    TestApp.sqlite3.set_dbfile(testdb)
    assert os.path.basename(TestApp.sqlite3.get_dbfile()) == os.path.basename(testdb)

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_connect(TestApp):
    # test that sqlite is creating a database file and closes it
    assert os.path.exists(TestApp.sqlite3.get_dbfile())

@pytest.mark.argv(['--debug'])
def test_ext_sqlite__get_table_info(TestApp):
    # test that the _get_table_info works properly
        model = sqlite_create_test_model()
        res = TestApp.sqlite3.create_table(model)

        # In assert we (for now) only check the name and the first field
        assert res['name'] == model['name']
        assert f"'{res['fields'][0]['name']}'" == model['fields'][0].split(' ')[0]

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_create_table(TestApp):
    # test that sqlite is creating a test table
    # and we can read this back from the database
    #
    model = TestApp.sqlite3.create_table(sqlite_create_test_model())
    assert model['name'] == 'test'

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_show_tables_no_tables(TestApp):
    # test show tables return on empty database

    # This should not return any tables
    ret = TestApp.sqlite3.show_tables()
    assert len(ret) == 0

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_show_tables_no_filter(TestApp):
    # Test the show_tables() function with no filter
    model1 = TestApp.sqlite3.create_table(sqlite_create_test_model(1))
    model2 = TestApp.sqlite3.create_table(sqlite_create_test_model(2))
    model3 = TestApp.sqlite3.create_table(sqlite_create_test_model(3))
    
    ret = TestApp.sqlite3.show_tables()
    assert ret[0]['name'] == 'test1'
    assert ret[1]['name'] == 'test2'
    assert ret[2]['name'] == 'test3'

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_show_tables_test_filter(TestApp):
    # Test the show_tables() function with no filter

    # First create 4 test tables.  test, test1, test3, test3
    model0 = TestApp.sqlite3.create_table(sqlite_create_test_model())
    model1 = TestApp.sqlite3.create_table(sqlite_create_test_model(1))
    model2 = TestApp.sqlite3.create_table(sqlite_create_test_model(2))
    model3 = TestApp.sqlite3.create_table(sqlite_create_test_model(3))
    
    # This shoudl only return 3 tables
    ret = TestApp.sqlite3.show_tables('test_')
    assert len(ret) == 3
    assert ret[0]['name'] == 'test1'
    assert ret[1]['name'] == 'test2'
    assert ret[2]['name'] == 'test3'

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_select_foo_as_string(TestApp):
    # Test basic select command
    ret = TestApp.sqlite3.select("'foo'")
    assert ret[0]["'foo'"] == 'foo'

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_select_bar_as_dict(TestApp):
    # Test basic select command
    ret = TestApp.sqlite3.select({'query': "'bar'"})
    assert ret[0]["'bar'"] == 'bar'


@pytest.mark.argv(['--debug'])
def test_ext_sqlite_select_count_as_string(TestApp):
    # Test select on actual table
    TestApp.sqlite3.create_table(sqlite_create_test_model())
    ret = TestApp.sqlite3.select("COUNT(id) FROM test")
    assert ret[0]['COUNT(id)'] == 0

@pytest.mark.argv(['--debug'])        
def test_ext_sqlite_select_count_as_dict(TestApp):
    # Test select on actual table 
    TestApp.sqlite3.create_table(sqlite_create_test_model())
    ret = TestApp.sqlite3.select({'query': 'COUNT(id)', 'from': 'test'})
    assert ret[0]['COUNT(id)'] == 0

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_insert_as_str(TestApp):
    # Test insert statment as a string
    TestApp.sqlite3.create_table(sqlite_create_test_model())
    rowsAffected = TestApp.sqlite3.insert("INTO test(date, txt, price) VALUES (CURRENT_DATE, 'test', 99.25)")
    assert rowsAffected == 1

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_insert_as_str_multiple_rows(TestApp):
    # Test insert statment as a string
    TestApp.sqlite3.create_table(sqlite_create_test_model())
    rowsAffected = TestApp.sqlite3.insert("INTO test(date, txt, price) VALUES (CURRENT_DATE, 'bannana', 1.25),(CURRENT_DATE, 'pear', 4.25),(CURRENT_DATE, 'apple', 99.25)")
    assert rowsAffected == 3

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_insert_as_dict(TestApp):
    # Test insert statment as a dict with single value
    TestApp.sqlite3.create_table(sqlite_create_test_model())
    rowsAffected = TestApp.sqlite3.insert(sqlite_create_insert_dict('test'))
    assert rowsAffected == 1

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_insert_as_dict_with_data(TestApp):
    # Test insert statment as a dict with single value
    TestApp.sqlite3.create_table(sqlite_create_test_model())
    rowsAffected = TestApp.sqlite3.insert(sqlite_create_insert_dict('test', True))
    assert rowsAffected == 1

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_insert_multiple_as_dict_with_empty_value(TestApp):
    # Test insert statment as a dict with multiple values and 
    # a trailing comma implying an empty value tuple
    TestApp.sqlite3.create_table(sqlite_create_test_model())
    ins = {
        'into': 'test',
        'cols': ('date', 'txt', 'price'),
        'values': [
            ('#CURRENT_DATE', 'banana', 3.25),
            ('#CURRENT_DATE', 'apple', 2349.95),
            ('#CURRENT_DATE', 'pear', 47.505),
            ('#CURRENT_DATE', 'raspberry', 25),         # Our false trailing comma
        ]
    }
    rowsAffected = TestApp.sqlite3.insert(ins)
    assert rowsAffected == 4


@pytest.mark.argv(['--debug'])
def test_ext_sqlite_select_from_multiple_tables_as_string(TestApp):
    # Test a select statment using two tables
    # first create two tables
    TestApp.sqlite3.create_table(sqlite_create_test_model(1))
    TestApp.sqlite3.create_table(sqlite_create_test_model(2))

    # Insert 1 row in test1 and two rows in test2
    TestApp.sqlite3.insert(sqlite_create_insert_dict('test1'))
    TestApp.sqlite3.insert(sqlite_create_insert_dict('test2'))
    TestApp.sqlite3.insert(sqlite_create_insert_dict('test2'))

    res = TestApp.sqlite3.select("* FROM test1,test2")
    assert len(res) == 2


@pytest.mark.argv(['--debug'])
def test_ext_sqlite_select_from_multiple_tables_as_dict_from_tuple(TestApp):
    # Test a select statment using two tables
    # first create two tables
    TestApp.sqlite3.create_table(sqlite_create_test_model(1))
    TestApp.sqlite3.create_table(sqlite_create_test_model(2))

    # Insert 1 row in test1 and two rows in test2
    TestApp.sqlite3.insert(sqlite_create_insert_dict('test1'))
    TestApp.sqlite3.insert(sqlite_create_insert_dict('test2'))
    TestApp.sqlite3.insert(sqlite_create_insert_dict('test2'))

    qry = {
        'query': '*',
        'from':  ('test1', 'test2')
    }
    res = TestApp.sqlite3.select(qry)
    assert len(res) == 2

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_select_from_multiple_tables_as_dict_from_list(TestApp):
    # Test a select statment using two tables
    # first create two tables
    TestApp.sqlite3.create_table(sqlite_create_test_model(1))
    TestApp.sqlite3.create_table(sqlite_create_test_model(2))

    # Insert 1 row in test1 and two rows in test2
    TestApp.sqlite3.insert(sqlite_create_insert_dict('test1'))
    TestApp.sqlite3.insert(sqlite_create_insert_dict('test2'))
    TestApp.sqlite3.insert(sqlite_create_insert_dict('test2'))

    qry = {
        'query': '*',
        'from':  ['test1', 'test2']
    }
    res = TestApp.sqlite3.select(qry)
    assert len(res) == 2

@pytest.mark.argv(['--debug'])
def test_sqlite_ext_select_with_clauses_dict(TestApp):
    # Test the select clauses function of the dict
    # Create our test model
    TestApp.sqlite3.create_table(sqlite_create_test_model())
    
    # insert 10 rows
    TestApp.sqlite3.insert(sqlite_create_10_insert_for_select_clauses())

    # Build our query
    qry = {
        'query': 'txt,price',
        'from': 'test',
        'clauses': {
            'where': 'price>0',
            'group_by': 'price'
        }
    }
    res = TestApp.sqlite3.select(qry)
    assert len(res) == 3

@pytest.mark.argv(['--debug'])
def test_ext_sqlite_create_index_as_string(TestApp):
    # test the create_index command
    TestApp.sqlite3.create_table(sqlite_create_test_model())
    ret = TestApp.sqlite3.create_index('test_idx ON test(id,date)')
    assert ret


