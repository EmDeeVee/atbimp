
import os
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from cement.utils import fs
from .core.exc import AtbImpAppError
from .controllers.base import Base
from .controllers.csv import Csv
from .controllers.duplicates import Duplicates
from .controllers.data import Data
from .controllers.imports import Imports
from cement import minimal_logger

LOG = minimal_logger(__name__)

# configuration defaults
#
# TODO: figure out how this works with a cement yaml config file
#
CONFIG = init_defaults('atbimp')
# CONFIG = init_defaults('atbimp', 'db.sqlite3')

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



def atbimp_post_argument_hook(app):
    LOG.debug('Inside AtbImp.post_setup hook!, setting up database')
    app.setupdb()


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
            Duplicates,
            Data,
            Imports
        ]

        # hooks
        hooks = [
            ('post_argument_parsing', atbimp_post_argument_hook )
        ]


    # Error codes.  We don't know what exit codes cement uses
    # so lets start ours at 128
    EC_FILE_NOT_FOUND = 128
    EC_PARAM_WRONG_FORMAT = 129
    EC_PARAM_MISSING = 130
    EC_RECORD_NOT_FOUND = 131
    EC_CONFIRMATION_CANCEL = 132
    EC_IMPORT_ID_NOT_FOUND = 133

    def setupdb(self):
        # Figure out our db file and let sqlite3 know
        if self.pargs.db is not None:
            self.dbFile = self.pargs.db
        else:
            self.dbFile = self.config.get(self.label, 'db_file')

        # Pave the way
        dbFile = fs.abspath(self.dbFile)
        dbDir = os.path.dirname(dbFile)
        if not os.path.exists(dbDir):
            os.makedirs(dbDir)

        # Connect to the database
        self.sqlite3.connect(self.dbFile)

        # Turn foreign_keys on  
        self.sqlite3.pragma('FOREIGN_KEYS = ON;')

        # check our invetory
        models = self.sqlite3.show_models()
        if len(models) == 0:
            # Empty db, we have to fill this
            #
            ret = self.sqlite3.import_script( f'{os.path.dirname(os.path.realpath(__file__))}/../config/initdb.sql')

            # Let's try again
            models = self.sqlite3.show_models()
            if len(models) == 0:
                # Give upp
                raise ValueError

        # We're good. Give our models to sqlite3
        # 
        self.sqlite3._models = {}
        for model in models:
            self.sqlite3._models.update({f"{model['name']}": model})
        





class AtbImpAppTest(TestApp,AtbImpApp):
    """A sub-class of AtbImpApp that is better suited for testing."""

    class Meta:
        label = 'atbimp'

    # Override models, so we don't automatically create them
    models = []
    indexes = False
    dbviews = False


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
