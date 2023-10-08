import os,random
from pytest import raises
from atbimp.main import AtbImpAppTest
'''
ext_sqlite3 tests.   Tests for the sqlite3 extention designed to
work with the cement framework. 

    TODO: Separate the tests from the AtbImpApp. 
    Still need cement some how.  Since the extention requires
    an (app) to work with.  Therefore standalone unit testing
    would require further abstraction and with that kinda kills 
    the design decision to create an extension for cement.

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

def sqlite_create_insert_dict(model, cnt=1):
    ''' Helper fuction to create dict for insert statment '''
    ins = {
        'into': model,
        'cols': ('date', 'txt', 'price'),
    }
    if cnt == 1:
        fruits=('banana', 'apple', 'pear', 'raspbery', 'fig', 'pineapple')
        fruitIdx = random.randint(0,5)
    
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
        assert res['name'] == model['name']  and f"'{res['fields'][0]['name']}'" == model['fields'][0].split(' ')[0]
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
        sqlite_cleanup(app)

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
        sqlite_cleanup(app)

def test_ext_sqlite_select_foo_as_string():
    # Test basic select command

    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        ret = app.sqlite3.select("'foo'")
        assert ret[0]["'foo'"] == 'foo'
        sqlite_cleanup(app)

def test_ext_sqlite_select_bar_as_dict():
    # Test basic select command

    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        ret = app.sqlite3.select({'query': "'bar'"})
        assert ret[0]["'bar'"] == 'bar'
        sqlite_cleanup(app)


def test_ext_sqlite_select_count_as_string():
    # Test select on actual table

    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        app.sqlite3.create_table(sqlite_create_test_model())
        ret = app.sqlite3.select("COUNT(id) FROM test")
        assert ret[0]['COUNT(id)'] == 0
        sqlite_cleanup(app)
        
def test_ext_sqlite_select_count_as_dict():
    # Test select on actual table 

    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        app.sqlite3.create_table(sqlite_create_test_model())
        ret = app.sqlite3.select({'query': 'COUNT(id)', 'from': 'test'})
        assert ret[0]['COUNT(id)'] == 0
        sqlite_cleanup(app)

def test_ext_sqlite_insert_as_str():
    # Test insert statment as a string

    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        app.sqlite3.create_table(sqlite_create_test_model())
        rowsAffected = app.sqlite3.insert("INTO test(date, txt, price) VALUES (CURRENT_DATE, 'test', 99.25)")
        assert rowsAffected == 1
        sqlite_cleanup(app)

def test_ext_sqlite_insert_as_str_multiple_rows():
    # Test insert statment as a string

    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        app.sqlite3.create_table(sqlite_create_test_model())
        rowsAffected = app.sqlite3.insert("INTO test(date, txt, price) VALUES (CURRENT_DATE, 'bannana', 1.25),(CURRENT_DATE, 'pear', 4.25),(CURRENT_DATE, 'apple', 99.25)")
        assert rowsAffected == 3
        sqlite_cleanup(app)

def test_ext_sqlite_insert_as_dict():
    # Test insert statment as a dict with single value

    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        app.sqlite3.create_table(sqlite_create_test_model())
        rowsAffected = app.sqlite3.insert(sqlite_create_insert_dict('test'))
        assert rowsAffected == 1
        sqlite_cleanup(app)

def test_ext_sqlite_insert_multiple_as_dict_with_empty_value():
    # Test insert statment as a dict with multiple values and 
    # a trailing comma implying an empty value tuple

    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)
        app.sqlite3.create_table(sqlite_create_test_model())
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
        rowsAffected = app.sqlite3.insert(ins)
        assert rowsAffected == 4
        sqlite_cleanup(app)


def test_ext_sqlite_select_from_multiple_tables_as_string():
    # Test a select statment using two tables
    
    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)

        # first create two tables
        app.sqlite3.create_table(sqlite_create_test_model(1))
        app.sqlite3.create_table(sqlite_create_test_model(2))

        # Insert 1 row in test1 and two rows in test2
        app.sqlite3.insert(sqlite_create_insert_dict('test1'))
        app.sqlite3.insert(sqlite_create_insert_dict('test2'))
        app.sqlite3.insert(sqlite_create_insert_dict('test2'))

        res = app.sqlite3.select("* FROM test1,test2")
        assert len(res) == 2
        sqlite_cleanup(app)


def test_ext_sqlite_select_from_multiple_tables_as_dict_from_tuple():
    # Test a select statment using two tables
    
    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)

        # first create two tables
        app.sqlite3.create_table(sqlite_create_test_model(1))
        app.sqlite3.create_table(sqlite_create_test_model(2))

        # Insert 1 row in test1 and two rows in test2
        app.sqlite3.insert(sqlite_create_insert_dict('test1'))
        app.sqlite3.insert(sqlite_create_insert_dict('test2'))
        app.sqlite3.insert(sqlite_create_insert_dict('test2'))

        qry = {
            'query': '*',
            'from':  ('test1', 'test2')
        }
        res = app.sqlite3.select(qry)
        assert len(res) == 2
        sqlite_cleanup(app)

def test_ext_sqlite_select_from_multiple_tables_as_dict_from_list():
    # Test a select statment using two tables
    
    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)

        # first create two tables
        app.sqlite3.create_table(sqlite_create_test_model(1))
        app.sqlite3.create_table(sqlite_create_test_model(2))

        # Insert 1 row in test1 and two rows in test2
        app.sqlite3.insert(sqlite_create_insert_dict('test1'))
        app.sqlite3.insert(sqlite_create_insert_dict('test2'))
        app.sqlite3.insert(sqlite_create_insert_dict('test2'))

        qry = {
            'query': '*',
            'from':  ['test1', 'test2']
        }
        res = app.sqlite3.select(qry)
        assert len(res) == 2
        sqlite_cleanup(app)

def test_sqlite_ext_select_with_clauses_dict():
    # Test the select clauses function of the dict

    with AtbImpAppTest() as app:
        app.run()
        sqlite_connect(app)

        # Create our test model
        app.sqlite3.create_table(sqlite_create_test_model())
        
        # insert 10 rows
        app.sqlite3.insert(sqlite_create_10_insert_for_select_clauses())

        # Build our query
        qry = {
            'query': 'txt,price',
            'from': 'test',
            'clauses': {
                'where': 'price>0',
                'group_by': 'price'
            }
        }
        res = app.sqlite3.select(qry)
        assert len(res) == 3
        sqlite_cleanup(app)

