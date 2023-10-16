
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


    # ========================================================================
    # Helper Functions
    # ========================================================================

    def _mkdict(self, labels, values):
        # Create a dict from two tuples
        # FIXME:  Discard and use dict(zip(...))
        #
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
        
        try:
            stmt = f"PRAGMA table_info({tbl})"
            res = self._cur.execute(stmt)
            fields=res.fetchall()
        except:
            raise ConnectionError

        ret = {'name': 'test', 'fields': []}
        labels = tuple(x[0] for x in self._cur.description)

        for fld in fields:
            # PRAGMA table_info returns a cid (column id) as the first
            # item in the tuple.  We have no use for that. Hence fld[1:]
            # and labels[1:]
            dictFld = self._mkdict(labels[1:], fld[1:])
            ret['fields'].append(dictFld)

        return ret


    def _values2str(self, values):
        # Convert tuple of values into a string, unquoting sqlite statments that start with a '#'
        ret = ""
        for value in values:
            if type(value) == str:
                if len(value) and value[0] == '#':
                    ret += f"{value[1:]}"       # Will only insert the contents of value
                else:
                    ret += f"'{value}'"         # make this an sqlite string literal 
            elif type(value) == int or type(value) == float:
                ret += f"{value}"
            else:
                raise ValueError
             
            ret += ', '                    
    
        # We couldn't use join() so remove the last 'comma space'
        # FIXME: Yes we can.  Just build a list first and then do join()
        #
        return ret[:-2]


    # ========================================================================
    # Interface Functions
    # ========================================================================
        
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
            filter = f"AND [name] LIKE '{filter}'"

        stmt = f"SELECT * FROM sqlite_schema WHERE NAME NOT LIKE 'sqlite_%' {filter}"
        try:
            self._cur.execute(stmt)
            models = self._cur.fetchall()
        except:
            raise ConnectionError
        
        labels = tuple(x[0] for x in self._cur.description)
        ret = []
        for model in models:
            model_info = self._mkdict(labels, model)
            ret.append(model_info)

        return ret


    def create_index(self, index):
        ''' Create index on Model.'''
        
        # Sanity check
        if len(index) == 0:
            raise ValueError
        
        # Create our statment.
        if type(index) == str:
            stmt = f"CREATE INDEX {index}"
        
        # execute our statment
        try:
            self._cur.execute(stmt)
            self._con.commit()
        except:
            raise ConnectionError
        
        return True
        
    def select(self, query):
        '''
        select()        select statment
        
        parameters:     query {string|dict}
                            {string}    with the select clause optionally with FROM or WHEN or 
                                        LIMIT or JOIN clauses

                            {dict}      dict in the form:
                                        {
                                            'query':    <select> ::= <str>|<dict>|<list>,
                                            'from':     [<from>  ::= <str>|<dict>|<list>],
                                            'where':    [<where> ::= <str>],
                                            'clauses': {                    # additional clauses
                                                'group_by': [<group_by_clause> ::= <str>],  
                                                'limit':    [<limit_clause> ::= <str>],    
                                                etc ...     [<valid_clause> ::= <str>]
                                            }
                                        }

                                The 'query' is mandatory. The 'from', 'where' and 'clauses'  are 
                                optional.  In the 'clauses' section, any valid SQL clause will go.  
                                The name of the clause will be  CAPITALIZED and undersocres 
                                replaced by spaces.
                                    so:  'group_by': 'date'         -> "GROUP BY date" 
                                    and: 'having': 'COUNT(id) > 3'  -> "HAVING COUNT(id) > 3

        Return:
                    Array of dicts
        '''            

        
        if type(query) == str:
            # query as string.  easy
            stmt = f"SELECT {query};"

        elif type(query) == dict:
            # query as dict.  A bit more work
            stmt = f"SELECT {query['query']}"
            if 'from' in query:
                # from section
                if type(query['from']) == str:
                    stmt += f" FROM {query['from']}"
                elif type(query['from']) == tuple or type(query['from']) == list:
                    stmt += f" FROM {','.join(query['from'])}"
                else:
                    raise ValueError
                
            if 'where' in query:
                # where section and
                if type(query['where']) == str:
                    stmt += f" WHERE {query['where']}"
                else:
                    raise ValueError

            # Clauses
            if 'clauses' in query:
                for clause in query['clauses']:
                    stmt += f" {clause.upper().replace('_', ' ')} {query['clauses'][clause]}"
        else:
            raise ValueError
        
        try:
            self._cur.execute(stmt)
            res = self._cur.fetchall()
        except:
            raise ConnectionError
        
        labels = tuple(x[0] for x in self._cur.description)
        ret = []
        for row in res:
            ret.append(self._mkdict(labels, row))

        return ret

    def insert(self, insert):
        '''
        insert()            Insert statment.

        parameters:     query {string|dict}
                            {string}    with the insert clause optionally requeres the insert 
                                        operation keyword like INTO or OR REPLACE.
                                        eg:)
                                            sqlite3.insert('INTO test(txt,price) VALUES('banana', 3.25))
                                            sqlite3.insert('OR REPLACE ......')

                                        basically a valid sqlite insert statement without the INSERT 
                                        keyword.

                            {dict}      dict in the form:
                                        {
                                            'into':    <table>,         # string
                                            'cols':    <cols>,          # tuple
                                            'values':  <tuple|list of tuples>
                                        }

                                        values can either be a tuple ('banana', 3.0) or a 
                                        list of tuples: [('banana', 3.0),('Apple', 3000.00)]

                                        or dict in the form:
                                        {
                                            'into':     <table>,
                                            'data':     <dict with key:value>
                                        }

                                        eg: 
                                            insert({'into': 'tbl', data{
                                                'fruit': 'banana',
                                                'price': 3.0
                                            }})

                                        When you want to use an Sqlite keyword as a value, you have
                                        to prefix it with a has (#), so python will validate it a a
                                        string but in the acutual build of the statement the enclosing
                                        quotes will be remved.

                                        eg: 
                                            {
                                                'into':     'todo',
                                                'cols':     ('date', 'item', 'notes'),
                                                'values':   ('#CURRENT_DATE', 'Picup my new car', 'Yeah!')
                                            }

        Returns:
            rows affected

        Raises:
            ValueError:         dict in improper format
            ConnectionError:    Error in statement.

        '''
        if type(insert) == str:
            stmt = f"INSERT {insert};"

        elif type(insert) == dict:
            stmt = f"INSERT INTO {insert['into']}"
            if 'data' in insert and len(insert['data']):
                # data takes precedence over the cols value pair
                columns = []
                values = []
                for col,val in insert['data'].items():
                    columns.append(col)
                    values.append(val)

                colstr = ", ".join(columns)
                stmt += f"({colstr})"

                # values we have to itterate since some need to be 
                # quoted, and some don't
                valstr = ""
                for val in values:
                    if type(val) == str:
                        if len(val) and val[0] == '#':
                            valstr += val[1:]  # skip the hash
                        else:
                            valstr += f"'{val}'"    # Quote it
                    elif type(val) == int or type(val) == float:
                        valstr += f"{val}"
                    
                    valstr += ","
                
                stmt += f" VALUES({valstr[:-1]})"

            else:
                # no data, so cols value pair
                if 'cols' in insert and len(insert['cols']):
                    stmt += f"{insert['cols']}"

                if 'values' in insert:
                    if type(insert['values']) == tuple:
                        stmt += f" VALUES ({self._values2str(insert['values'])})"

                    elif type(insert['values']) == list:
                        # Handle list of tuples
                        stmt += f" VALUES"
                        for row in insert['values']:
                            if type(row) == tuple:
                                stmt += f"({self._values2str(row)}),"
                            else:
                                raise ValueError
                            
                        # Remove trailing comma
                        stmt = stmt[:-1]

                    else:
                        raise ValueError
        else:
            raise ValueError

        try:
            self._cur.execute(stmt)
            self._con.commit()
        except:
            raise ConnectionError

        return self._cur.rowcount        

        
    def close(self):
        ''' close the connection '''
        self._con.close()
        self._con = None
    

def load(app):
    # do something to extend cement
    app.interface.define(DatabaseInterface)
    app.handler.register(SQLite3Handler)
    app.hook.register('pre_run', sqlite3_pre_run_hook)

