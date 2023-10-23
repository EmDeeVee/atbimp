
import os
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from cement.utils import fs
from .core.exc import AtbImpAppError
from .controllers.base import Base
from .controllers.csv import Csv

# configuration defaults
#
# TODO: figure out how this works with a cement yaml config file
#
CONFIG = init_defaults('atbimp', 'db.sqlite3')

# CONFIG['atbimp']['db_file'] = '~/.atbimp/transactions.db3'
CONFIG['atbimp']['db_file'] = './transactions.db3'


# exp_tbl_cols:
#
# This is (our version) of the rows in an ATB export file.  We changed
# the names slightly, getting rid of spaces and capitals to be more 
# database like.
#
# This list of field columns will only be used by the export function
# if no header line is found.
#
CONFIG['atbimp']['exp_tbl_cols'] = [
    'date',                     #0
    'account_rtn',              #1
    'account_number',           #2
    'transaction_type',         #3
    'customer_ref_number',      #4
    'debit_amount',             #5
    'credit_amount',            #6
    'running_balance_amount',   #7
    'extended_text',            #8
    'bank_reference_number'     #9
]

# db.accounts.tbl:
#
# In our version of the database there will be a list of acounts in the 'accounts' table.
# This table will hold a list of all bank accounts found. 
#
CONFIG['db.sqlite3']['accounts'] = [
    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL",
    "'alias' TEXT",                     # Last 4 digits of our account number
    "'acct_routing' TEXT",              # bank routing info
    "'acct_number' TEXT",               # your account number
    "'nick_name' TEXT"                 # a nick name that can be provided by the user
]

# db.months.tbl
#
# We put the year-month porttion of the data into a separate table, just to speed up
# looking for all transaction of a particular month.
CONFIG['db.sqlite3']['months'] = [
    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL",
    "'year' INTEGER",                   # Last 4 digits of our account number
    "'month' INTEGER",                  # bank routing info
]

# db.imports.table
#
# logging all the imports that have been done, so in case of duplicates we can 
# trace back who did what
#
CONFIG['db.sqlite3']['imports'] = [
    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL",
    "'time_stamp' TEXT DEFAULT CURRENT_TIMESTAMP",
    "'source' TEXT"
]

# db.duplicates.table
#
# basically the same layout as the cvs file, with as extras
# the id and the foreign_key for the import log
#
CONFIG['db.sqlite3']['duplicates'] = [
    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL",
    "'import_id' INTEGER",      # The link with the imports table
    "'date' TEXT",                    
    "'account_rtn' TEXT",             
    "'account_number' TEXT",          
    "'transaction_type' TEXT",        
    "'customer_ref_number' TEXT",     
    "'debit_amount' TEXT",            
    "'credit_amount' TEXT",           
    "'running_balance_amount' TEXT",  
    "'extended_text' TEXT",           
    "'bank_reference_number' TEXT"    
]

# db.transactions.table:
#
CONFIG['db.sqlite3']['transactions'] = [
    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL",
    "'account_id' INTEGER",    # The link with the accounts table
    "'month_id' INTEGER",      # The link to months table
    "'import_id' INTEGER",      # The link with the imports table
    "'date' TEXT",
    "'transaction_type' TEXT",
    "'customer_ref_number' TEXT",
    "'amount' REAL",
    "'dc' TEXT",                # is the amount Debit or Credit (D/C)
    "'balance' REAL",           # running balance
    "'description' TEXT",
    "'bank_reference' TEXT"
]

# db.transactions.indexes
# 
# a list of indexes to create.  Set app.indexes to true in order to 
# automatically create them
#
CONFIG['db.sqlite3']['indexes'] = [
    {
        'index':    'trans_idx',
        'model':    'transactions',
        'fields':   'date,amount,balance'
    }
]


class AtbImpApp(App):
    """ATB CSV Import and List Application primary application."""

    class Meta:
        label = 'atbimp'

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
            'atbimp.ext.ext_sqlite3',
        ]

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        # register handlers
        handlers = [
            Base,
            Csv,
        ]

        # hooks
        hooks = []



    # models to use in our app.  All models listed here wil expect a 
    # config["model"]["{modelName}"] setting with the layout.
    # these models will automatically created if they don't exist
    models = [
        'months',
        'transactions',
        'accounts',
        'imports',
        'duplicates'
    ]

    indexes = True

    # Error codes.  We don't know what exit codes cement uses
    # so lets start ours at 128
    EC_FILE_NOT_FOUND = 128





class AtbImpAppTest(TestApp,AtbImpApp):
    """A sub-class of AtbImpApp that is better suited for testing."""

    class Meta:
        label = 'atbimp'

    # Override models, so we don't automatically create tehm
    models = []
    indexes = False


def main():
    with AtbImpApp() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except AtbImpAppError as e:
            print('AtbImpAppError > %s' % e.args[0])
            app.exit_code = 2

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
