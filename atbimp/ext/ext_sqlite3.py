
'''
SQlite 3 wrapper for cement
'''
import os
from cement.core.interface import Interface
from cement.core import handler
from cement import minimal_logger
from cement.utils import fs

LOG = minimal_logger(__name__)

def sqlite3_pre_run_hook(app):
    # Add the sqlite3 member to app and attach it with the
    # database.sqlite3 handler.
    #
    LOG.debug('Inside sqlite3_pre_run_hook! Seting up sqlite3 handler')
    _handler = app.handler.get('db', 'sqlite3')
    app.sqlite3=_handler()

def sqlite3_pre_argument_parsing_hook(app):
    LOG.debug('Inside sqlite3_post_run_hook! Setting up sqlite3 class')

class DatabaseInterface(Interface):
    """
    This class Impements the Database Interfece witch is 
    as of now `Not implemented in cement'
    """
    class Meta:
        interface='db'

    

class SQLite3Handler(DatabaseInterface, handler.Handler):
    '''
    SQLite3(db_file)    (YASW) Yet another SQLite Wrapper
    parameters:
        db_file:        path to the slite.db file to use

    '''

    class Meta:
        label = "sqlite3"
        sqlite3_module = 'sqlite3'
        interface='db'

    _sqlite3 = None                 # The module
    _db_file= "mydatabase.db3"      # internal member hoding the db file
    _con = None                     # db connection
    _cur = None                     # db cursor
    

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._sqlite3 =  __import__(self.Meta.sqlite3_module, 
                                   globals(), locals(), 0)

    def __setup__(self, app):
        super()._setup(app)

    def set_dbfile(self, db_file: str):
        ''' set the db_file and create parent dir if needed '''
        self._db_file = fs.abspath(db_file)
        db_dir = os.path.dirname(self._db_file)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        

    def get_dbfile(self): 
        ''' get the active db_file'''
        return self._db_file
    
    def connect(self):
        '''
        Connect to the given database
        
        raises:
            ConnectionEror:         No db file given
            ConnectionOrror:        Error opening db
        '''
        if len(self._db_file):
            try:
                self._con = self._sqlite3.connect(self._db_file)
                self._cur = self._con.cursor()
            except:
                raise ConnectionError('Error opening db file')
        else:
            raise ConnectionError('No db file given')

    def close(self):
        ''' close the connection '''
        self._con.close()
        self._con = None
    

def load(app):
    # do something to extend cement
    app.interface.define(DatabaseInterface)
    app.handler.register(SQLite3Handler)
    app.hook.register('pre_run', sqlite3_pre_run_hook)
    # app.hook.register('pre_argument_parsing', sqlite3_pre_argument_parsing_hook)

