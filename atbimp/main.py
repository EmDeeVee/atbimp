
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
CONFIG = init_defaults('atbimp')
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

# db_accounts_tbl:
#
# In our version of the database there will be a list of acounts in the 'accounts' table.
# This table will hold a list of all back accounts found.  The transactions will be placed
# in seperate tables, one per account.
#
CONFIG['atbimp']['db_accounts_tbl_cols'] = [
    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL",
    "'alias' TEXT",                     # Last 4 digits of our account number
    "'acct_routing' TEXT",              # bank routing info
    "'acct_number' TEXT"                # your account number
]

# db_account_tbl_cols:
#
# Table structure of each account table.  Tables will be named the alias of the account.
#
CONFIG['atbimp']['db_account_tbl_cols'] = [
    "'accounts_id' INTEGER",
    "'date' TEXT",
    "'transaction_type' TEXT",
    "'customer_ref_number' TEXT",
    "'amount' REAL",
    "'dc' TEXT",                # is the amount Debit or Credit (D/C)
    "'balance' TEXT",           # running balance
    "'description' TEXT",
    "'bank_reference' TEXT"
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

    # Error codes.  We don't know what exit codes cement uses
    # so lets start ours at 128
    EC_FILE_NOT_FOUND = 128



class AtbImpAppTest(TestApp,AtbImpApp):
    """A sub-class of AtbImpApp that is better suited for testing."""

    class Meta:
        label = 'atbimp'


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
