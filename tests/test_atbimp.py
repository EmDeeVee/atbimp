import os
from pytest import raises
from atbimp.main import AtbImpAppTest

def test_atbimp():
    # test atbimp without any subcommands or arguments
    with AtbImpAppTest() as app:
        app.run()
        assert app.exit_code == 0


def test_atbimp_debug():
    # test that debug mode is functional
    argv = ['--debug']
    with AtbImpAppTest(argv=argv) as app:
        app.run()
        assert app.debug is True

def test_atbimp_ext_sqlite():
    # test that sqlite extension is functional
    argv = ['--debug']
    with AtbImpAppTest(argv=argv) as app:
        app.run()
        app.sqlite3.set_dbfile('./tests/test.db3')
        assert os.path.basename(app.sqlite3.get_dbfile()) == 'test.db3'

def test_atbimp_ext_sqlite_connect():
    # test that sqlite is creating a database file
    with AtbImpAppTest() as app:
        app.run()
        app.sqlite3.set_dbfile('./tests/test.db3')
        db_file=app.sqlite3.get_dbfile()
        app.sqlite3.connect()
        assert os.path.exists(db_file)
        os.remove(db_file)
        
# def test_command1():
#     # test command1 without arguments
#     argv = ['command1']
#     with AtbImpAppTest(argv=argv) as app:
#         app.run()
#         data,output = app.last_rendered
#         assert data['foo'] == 'bar'
#         assert output.find('Foo => bar')


#     # test command1 with arguments
#     argv = ['command1', '--foo', 'not-bar']
#     with AtbImpAppTest(argv=argv) as app:
#         app.run()
#         data,output = app.last_rendered
#         assert data['foo'] == 'not-bar'
#         assert output.find('Foo => not-bar')
