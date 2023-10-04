
'''
SQlite 3 wrapper for cement.  
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

    def _mkdict(self, labels, values):
        # Create a dict from two tubles
        if len(labels) > 0 and len(values) > 0 and len(labels) == len(values):
            ret = {}
            for i,value in enumerate(values):
                ret[labels[i]] = value
        else: 
            return None
        
        return ret

    def _get_table_info(self, tbl):
        # get table fields
        # 
        # Return will be something like this
        # {
        #     "name": "test",
        #     "fields": [
        #         {
        #             "name": "id",
        #             "type": "INTEGER",
        #             "notnull": 0,
        #             "dflt_value": null,
        #             "pk": 0
        #         },
        #         {
        #             "name": "date",
        #             "type": "DATE",
        #             "notnull": 0,
        #             "dflt_value": null,
        #             "pk": 0
        #         },
        #         {
        #             "name": "txt",
        #             "type": "TEXT",
        #             "notnull": 0,
        #             "dflt_value": null,
        #             "pk": 0
        #         },
        #         {
        #             "name": "price",
        #             "type": "DECIMAL(10,2)",
        #             "notnull": 0,
        #             "dflt_value": null,
        #             "pk": 0
        #         }
        #     ]
        # }
        if len(tbl) == 0:
            raise ValueError
        
        labels = ('name', 'type', 'notnull', 'dflt_value', 'pk')
        try:
            stmt = f"PRAGMA table_info({tbl})"
            res = self._cur.execute(stmt)
            fields=res.fetchall()
        except:
            raise ConnectionError

        ret = {'name': 'test', 'fields': []}
        for fld in fields:
            # PRAGMA table_info returns a cid (column id) as the first
            # item in the tuple.  We have no use for that. Hence fld[1:]
            #
            dictFld = self._mkdict(labels, fld[1:])
            ret['fields'].append(dictFld)

        return ret

        

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
        if len(self._db_file) == 0:
            raise ConnectionError('No db file given')
        else:
            try:
                self._con = self._sqlite3.connect(self._db_file)
                self._cur = self._con.cursor()
            except:
                raise ConnectionError('Error opening db file')
            
    def create_table(self, dictTable):
        '''
        create_table()          Creates a new table

        Paremeters:
            dictTable:          dict to describe model. eg:
        
                                test_model={
                                    'name':     'test', 
                                    'fields':   [
                                        "'id' INTEGER",
                                        "'date' DATE",
                                        "'txt' TEXT",
                                        "'price' DECIMAL(10,2)"
                                    ]
                                }

        Returns:
            dictTable as returned by PRAGMA table_info()

        Raises:
            KeyError:         when dict is of improper format

        '''
        # do some basic sanity checking on the dict
        #
        if len(dictTable) < 1:
            if (len(dictTable['name']) < 1) and (len(dictTable['fields']) < 1):
                # We should have a KeyError exeption by now
                return None
        
        # Let's get to work.
        sFieldList = ", ".join(dictTable['fields'])
        stmt = f"CREATE TABLE {dictTable['name']} ({sFieldList})"
        try:
            self._cur.execute(stmt)
            self._con.commit()
        except:
            raise ConnectionError
        
        return self._get_table_info(dictTable['name'])
        

    def show_tables(self, filter=""):
        '''
        show_tables()           Show available tables in db
        
        Parameters:
            filter:             Optinal filter, wich will be added to the WHERE clause
                                eg "test%"
                                
        Retuns:                 An Array of dicts containing the table_info for each table found
        '''

        if len(filter):
            filter = f"WHERE [name] LIKE '{filter}'"

        stmt = f"SELECT * FROM sqlite_schema {filter}"
        try:
            self._cur.execute(stmt)
            self._con.commit()
            models = self._cur.fetchall()
        except:
            raise ConnectionError
        
        labels = ('type', 'name', 'tbl_name', 'rootpage', 'sql')
        ret = []
        for model in models:
            model_info = self._mkdict(labels, model)
            ret.append(model_info)

        return ret

                                                  
                        
    def close(self):
        ''' close the connection '''
        self._con.close()
        self._con = None
    

def load(app):
    # do something to extend cement
    app.interface.define(DatabaseInterface)
    app.handler.register(SQLite3Handler)
    app.hook.register('pre_run', sqlite3_pre_run_hook)

