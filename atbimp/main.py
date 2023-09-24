
import os
from sqlalchemy import create_engine, text
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from cement.utils import fs
from .core.exc import AtbImpAppError
from .controllers.base import Base
from .controllers.csv import Csv

# configuration defaults
CONFIG = init_defaults('atbimp')
# CONFIG['atbimp']['db_file'] = '~/.atbimp/transactions.db3'
CONFIG['atbimp']['db_file'] = './transactions.db3'
CONFIG['atbimp']['create_table_import'] = """
CREATE TABLE import (
    "Date" DATE, 
    "account_rtn" TEXT, 
    "account_number" TEXT, 
    "transaction_type" TEXT, 
    "customer_ref_number" TEXT, 
    "debit_amount" DECIMAL (10, 2), 
    "credit_amount" DECIMAL (10, 2), 
    "running_balance_amount" DECIMAL (10, 2), 
    "extended_text" TEXT, 
    "bank_reference_number" TEXT
)
"""
CONFIG['atbimp']['create_table_transactions'] = """
CREATE TABLE transactions (
    "transaction_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "date" DATE, 
    "account_rtn" TEXT, 
    "account_number" TEXT, 
    "transaction_type" TEXT, 
    "customer_ref_number" TEXT, 
    "debit_amount" DECIMAL (10, 2), 
    "credit_amount" DECIMAL (10, 2), 
    "running_balance_amount" DECIMAL (10, 2), 
    "extended_text" TEXT, 
    "bank_reference_number" TEXT
)
"""
CONFIG['atbimp']['create_idx_transactions'] = """
CREATE INDEX idx_transaction_id ON transactions ("transaction_id")
"""

def extend_sqla(app):
    app.log.info('Extending App with SQLAlchemy (Sqlite3)')
    db_file = app.config.get('atbimp', 'db_file')

    # ensure that we extend the full path
    db_file = fs.abspath(db_file)
    app.log.info("Database file is in: %s" % db_file)

    # ensure that the parent directory exists
    db_dir = os.path.dirname(db_file)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Create our db engine
    try:
        db=create_engine("sqlite+pysqlite:///%s" % db_file)
    except:
        app.log.error('Cannot create DB engine! Aborting ... check config or requirements')
    else:

        # Create our actual db file if none is there
        if not os.path.exists(db_file):
            app.log.info('Initial DB configuration')

            # Create our tables
            try:
                with db.connect() as conn:
                    app.log.info('-- Creating table_import ...')
                    conn.execute(text(app.config.get('atbimp', 'create_table_import')))
                    app.log.info('-- Creating table_transactions ...')
                    conn.execute(text(app.config.get('atbimp', 'create_table_transactions')))
                    app.log.info('-- Creating idx_transactions ...')
                    conn.execute(text(app.config.get('atbimp', 'create_idx_transactions')))
            except:
                app.log.error('Cannot create tables!')

                # Mount it to our app
                app.extend('db', db)

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
        hooks = [
            ('post_argument_parsing', extend_sqla)
        ]


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
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
