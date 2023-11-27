
'''
SQlite 3 wrapper for cement.  
'''
from cement.core.interface import Interface
from cement.core import handler
from cement import minimal_logger

LOG = minimal_logger(__name__)



def sqlite3_post_run_hook(app):
    LOG.debug('Inside sqlite3_post_argument_hook! Closing the database')
    # Close database
    if app.sqlite3._con:
        app.sqlite3.close()


def sqlite3_post_setup_hook(app):
    LOG.debug('Inside sqlite3_post_setup_hook! Setting up sqlite3 handler')
    # setup our sqlite3 var
    handle = app.handler.get('db', 'sqlite3')
    app.sqlite3 = handle()
    app.sqlite3._sqlite3 =  __import__(app.sqlite3.Meta.sqlite3_module, globals(), locals(), 0)


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
    _db_file= None                  # internal member hoding the db file
    _con = None                     # db connection
    _cur = None                     # db cursor
    _models = []                    # list of models we use
    


    # ========================================================================
    # Helper Functions
    # ========================================================================

    # _trim_sql(stmt);
    # 
    # Trim a raw sql statement.  Remove newlines and exesive space
    #
    def _trim_sql(self,stmt):
        lRet=stmt.split('\n')
        lRet=[line.strip() for line in lRet]
        ret = ' '.join(lRet).strip()

        return ret


    def _escape_from(self,from_clause):
        '''
        _escape_from(from)

        ``from'': str|tuple|list can be in the following formats
            - "tabel"
            - "tabel1, "table2, table3"
            - "table t"
            - "table1 t1, table2 t2, table3 t3"
        regadless of the fact if their presentent as a string, list or tuple.

        In all cases the table name has to be escaped with quotes to avoid a
        collision with an sqlite keyword.  Such as the table ``transaction'' 
        in the atbimp project.
        '''

        # first seperate the tables
        if type(from_clause) == str:
            tables = from_clause.split(',')
        elif type(from_clause) == list or type(from_clause) == tuple:
            tables = from_clause
        
        ret=[]
        # separate the tables from the aliases.
        for i,table in enumerate(tables):
            tblAlias = table.split()
            val=f"'{tblAlias[0]}'"
            if len(tblAlias) > 1:
                val += f" {tblAlias[1]}"
            ret.append(val)

        
        return ",".join(ret)


    def _lookup_inventory(self, inventory_type, filter=''):
        # Lookup tables, views and indexes in sqlite_master table.
        # 
        
        # internal functions.  No param checking.  Should be oke
        if len(filter):
            filter = f"AND tbl_name LIKE '{filter}'"

        stmt = f"SELECT * FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' AND type='{inventory_type}' {filter};"
        try:
            self._cur.execute(stmt)
            inventory = self._cur.fetchall()
        except:
            raise ConnectionError
        
        ret = []
        for item in inventory:
            if inventory_type == 'table':
                ret.append(self._get_model_info(item[1]))
            elif inventory_type == 'index':
                ret.append(self._get_index_info(item[1]))
            else:
                # TODO: Where is get_view_info() ???
                pass

        return ret



    def _get_model_info(self, model):
        # get table fields
        # 
        # Return will be something like this
        # {
        #     "name": "testdb",
        #     "fields": {
        #         "id": {
        #             "cid": 0,
        #             "name": "id",
        #             "type": "INTEGER",
        #             "notnull": 0,
        #             "dflt_value": null,
        #             "pk": 1
        #         },
        #         "date": {
        #             "cid": 1,
        #             "name": "date",
        #             "type": "DATE",
        #             "notnull": 0,
        #             "dflt_value": null,
        #             "pk": 0
        #         },
        #         "txt": {
        #             "cid": 2,
        #             "name": "txt",
        #             "type": "TEXT",
        #             "notnull": 0,
        #             "dflt_value": null,
        #             "pk": 0
        #         },
        #         "price": {
        #             "cid": 3,
        #             "name": "price",
        #             "type": "DECIMAL(10,2)",
        #             "notnull": 0,
        #             "dflt_value": null,
        #             "pk": 0
        #         }
        #     }
        # }
        if len(model) == 0:
            raise ValueError
        
        if type(model) == str:
            modelName = model
        elif type(model) == dict:
            modelName = model['name']

        try:
            stmt = f"PRAGMA table_info('{model}')"
            res = self._cur.execute(stmt)
            fields=res.fetchall()
        except:
            raise ConnectionError

        ret = {'name': modelName, 'fields': {} }
        labels = tuple(x[0] for x in self._cur.description)

        for fld in fields:
            fdict=dict(zip(labels,fld))
            ret['fields'].update({f'{fdict["name"]}': fdict})

        return ret

    def _get_index_info(self, index):
        # Will return a dict {'name': <name>, 'fields': [<fld>,<fld>,...]}
        #
        if len(index) == 0:
            raise ValueError
        
        if type(index) == str:
            indexName = index
        elif type(index) == dict:
            indexName = index['index']
        else:
            raise ValueError
        
        try:
            stmt = f"PRAGMA index_info('{indexName}');"
            res = self._cur.execute(stmt)
            fields=res.fetchall()
        except:
            raise ConnectionError

        ret = {'name': indexName, 'fields': [] }
        for row in fields:
            ret['fields'].append(row[2])

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
        # TODO: Yes we can.  Just build a list first and then do join()
        #
        return ret[:-2]


    # ========================================================================
    # Interface Functions
    # ========================================================================
        
    def dbfile(self): 
        ''' get the active db_file'''
        return self._db_file
    
    def connect(self, dbfile):
        '''
        Connect to the given database

        Parameters:
            dbfile:                 (str)sqlite db file to use
        
        raises:
            ValueError:             No db file given
            ConnectionError:        Error opening db
        '''
        if len(dbfile) == 0:
            raise ValueError('No db file given')
        else:
            try:
                self._con = self._sqlite3.connect(dbfile)
                self._cur = self._con.cursor()
            except:
                raise ConnectionError('Error opening db file')

            self._db_file = dbfile

    def pragma(self, pragma):
        '''
        pragma()                send a pragma to the engine
                                eg) pragma('FOREIGN_KEYS = ON')

        Parameters:
            pragma:             (str) pragma and it's value

        Returns:
            <mixed>                 Returns what the fetchall() returns

        Raises:
            ValueError:             No pragma given
            ConnectionError:        wrong pragma string
        '''
        if len(pragma) == 0:
            raise ValueError('No pragma given')
        else:
            try:
                stmt = f"PRAGMA {pragma}"
                res = self._cur.execute(stmt)
                ret = res.fetchall()
            except:
                raise ConnectionError('Wrong pragma string')
            
            return ret

    def import_script(self, sqlfile):
        stmt = ""
        ret = None
        try:
            with open(sqlfile) as f:
                stmt = f.read()
            self._cur.executescript(stmt)
        except:
            raise ConnectionError
            
            
    def create_model(self, dictModel):
        '''
        create_model()          Creates a new table

        Paremeters:
            dictModel:          dict to describe model. eg:
        
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
            dictModel as returned by PRAGMA table_info()

        Raises:
            KeyError:         when dict is of improper format

        '''
        # do some basic sanity checking on the dict
        #
        if len(dictModel) < 1:
            if (len(dictModel['name']) < 1) and (len(dictModel['fields']) < 1):
                # We should have a KeyError exeption by now
                return None
        
        # Let's get to work.
        sFieldList = ", ".join(dictModel['fields'])
        stmt = f"CREATE TABLE {dictModel['name']} ({sFieldList})"
        try:
            self._cur.execute(stmt)
            self._con.commit()
        except:
            raise ConnectionError
        
        return self._get_model_info(dictModel['name'])
        

    def show_models(self, filter=""):
        '''
        show_models()           Show available tables in db
        
        Parameters:
            filter:             Optinal filter, wich will be added to the WHERE clause
                                eg "test%"
                                
        Retuns:                 An Array of dicts containing the table_info for each table found
        '''
        return self._lookup_inventory('table', filter)
    
    def model(self, modelName: str):
        '''
        model(modelName: str)       Get cached info of model
        '''
        if len(modelName) == 0:
            raise ValueError('No model name given')

        # BUG: what is this?  model = 'poe' ???? 
        model = 'poe'
    

    def create_index(self, index, bUnique=False, bIfNotEists=False):
        ''' 
        create_index() -> bSuccess     Create index on Model.

        parameters:
            index:          <string>
                            eg: "test_idx ON test(price)"
            bUnique:        <bool> (default False)
                            add the UNIQUE constraint
            bIfNotExists    <bool> (defualt False)
                            add the 'IF NOT EXISTS' constrained.

        or: 
            index:          <dict>  
                            pars: bUnique, bIfnotExist will be ignored
                            {
                                'index':        'test_idx',
                                'model':        'test',
                                'fields':       'date,price',
                                'unique':       True,    # optional
                                'ifnotexists':  True,    # optional
                            }                                

        Returns:
            True, or raises error

        Raises:
            ValueError:         When index param is empty
            ConnectionError:    error in SQL statement.
        '''
        if type(index) == str:
            if len(index) == 0:
                raise ValueError
            
        elif type(index) == dict:
            if 'unique' in index:
                bUnique = index['unique']
            if 'ifnotexists' in index:
                bIfNotEists = index['ifnotexists']
        else:
            raise ValueError

        unique = ''
        if bUnique: 
            unique = "UNIQUE"

        ifnotexists = ''
        if bIfNotEists:
            ifnotexists = 'IF NOT EXISTS'


        # Create our statment.
        stmt = f"CREATE {unique} INDEX {ifnotexists} "
        if type(index) == str:
             stmt+=index
        elif type(index) == dict:
            stmt+=f"{index['index']} ON {index['model']}({index['fields']})"
    
        stmt+=';'
        
        # execute our statment
        try:
            self._cur.execute(stmt)
            self._con.commit()
        except:
            raise ConnectionError
        
        return True
        
    def show_indexes(self, table=''):
        '''
        show_indexes()          Show available indexes in db
        
        Parameters:
            table:              Optinal filter. Show only the indexes for that table
                                eg "test%"
                                
        Retuns:                 An Array of dicts containing the table_info for each table found
        '''
        return self._lookup_inventory('index', table)
    

    def create_view(self, dbView):
        # TODO: Write test and make more enable the accepting a dict to create

        # do some basic sanity checking on the dict
        # FIXME: assume dbView as dict for now
        if len(dbView) < 1:
            if (len(dbView['name']) < 1) and (len(dbView['fields']) < 1):
                # We should have a KeyError exeption by now
                return None
            
        if 'ifnotexists' in dbView:
            bIfNotEists = dbView['ifnotexists']

        ifnotexists = ''
        if bIfNotEists:
            ifnotexists = 'IF NOT EXISTS'


        # Create our statment.
        # FIXME: asume dbView.sql has it all
        if 'sql' in dbView:
            stmt = self._trim_sql(dbView['sql'])
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
                                            'join':     [<join>  ::= <str>|<list>,
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
            if 'from' in query and len(query['from']):
                stmt += f" FROM {self._escape_from(query['from'])}"
                
            if 'join' in query and len(query['join']):
                if type(query['join']) == str:
                    stmt += f" JOIN {query['join']}"
                elif type(query['join']) == list:
                    joinClause = " ".join(query['join'])
                    stmt += " JOIN " + " ".join(joinClause)
                
            if 'where' in query and len(query['where']):
                # where section and
                if type(query['where']) == str:
                    stmt += f" WHERE {query['where']}"
                else:
                    raise ValueError

            # Clauses
            if 'clauses' in query:
                for clause in query['clauses']:
                    if len(clause):
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
            ret.append(dict(zip(labels, row)))

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
            stmt = f"INSERT INTO '{insert['into']}'"
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

    def update(self,update):
        '''
        update()            Update statment
        
        parameters:         update {string|dict}
                                {string}    with the update statment, optinally requires the update
                                            operation keywords like OR ABORT, OR FAIL, OR ROLLBACK
                                            eg:)
                                                sqlite.update('test SET txt='not available')
                                                sqlite.update('test OR ABORT SET price=100 WHERE id=1)
                                            
                                {dict}      dict in the form:
                                            {
                                                'update':   <string> with table name
                                                'set':      <string|dict> containing the values to be updated
                                                'where':    <string> with where clause
                                            }
                                            eg:)
                                                sqlite.update({'update': 'test', 'set': "txt='not available"})
                                                sqlite.update({'update': 'test', 'set': 'price=100', 'where': 'id=1})
                                                update = {
                                                    'update': 'test',
                                                    'set':    {'price': 49.90, 'txt': 'Discounted!'},
                                                    'where':  'price=99.25'
                                                }
        Returns:
            rows affected

        Raises:
            ValueError:         dict in improper format
            ConnectionError:    Error in statement.

        '''
        if type(update) == str:
            stmt = f"UPDATE {update}"
        elif type(update) == dict:
            stmt = f"UPDATE '{update['update']}'"
            if type(update['set']) == str:
                stmt += f" SET {update['set']}"
            elif type(update['set']) == dict:
                setLst=[]
                for itm in list(zip(update['set'].keys(),update['set'].values())):
                    setLst.append(f"{itm[0]}='{itm[1]}'")
                    
                stmt += " SET " + ", ".join(setLst)
            else:
                raise ValueError
            
            if type(update['where']) == str:
                stmt += f" WHERE {update['where']}"
            else:
                raise ValueError
            
        else:
            raise ValueError
        
        # Execute the query
        try:
            self._cur.execute(stmt)
            self._con.commit()
        except:
            raise ConnectionError

        return self._cur.rowcount        
        
                                                
    def delete(self,delete):
        '''
        delete()            Delete statment.

        parameters:     delete {string|dict}
                            {string}    with the delete clause, optionally requieres the delete 
                                        operation keywords like FROM, WHERE, ORDER BY or LIMIT.
                                        eg:)
                                            sqlite3.delete('FROM test'))
                                            sqlite3.delete('FROM test WHERE id>10')

                                        basically a valid sqlite insert statement without the DELETE 
                                        keyword.

                            {dict}      dict in the form:
                                        {
                                            'from':     <string>|<tuple>|list, 
                                            'where':    <string>,
                                            'order_by': <string>,
                                            'limit':    <string>
                                        }

                                        eg: 
                                            delete(
                                                'from': 'test',
                                                'where': 'id>10'
                                            })

        Returns:
            rows affected

        Raises:
            ValueError:         dict in improper format
            ConnectionError:    Error in statement.

        '''
        if type(delete) == str:
            stmt = f"DELETE {delete}"

        elif type(delete) == dict:
            stmt = f"DELETE"

            if 'from' in delete and len(delete['from']):
                # # from section
                # if type(delete['from']) == str:
                #     stmt += f" FROM '{delete['from']}'"
                # elif type(delete['from']) == tuple or type(delete['from']) == list:
                #     lst = "','".join(delete['from'])
                #     stmt += f" FROM '{lst}'"
                # else:
                #     raise ValueError
                stmt += f" FROM {self._escape_from(delete['from'])}"
                
            if 'where' in delete and len(delete['where']):
                # where section and
                if type(delete['where']) == str:
                    stmt += f" WHERE {delete['where']}"
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
    app.hook.register('post_setup', sqlite3_post_setup_hook)
    app.hook.register('post_run', sqlite3_post_run_hook)

