
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
CONFIG['atbimp']['db_tbl_cols'] = [
    'date', 
    'account_rtn', 
    'account_number', 
    'transaction_type', 
    'customer_ref_number', 
    'debit_amount', 
    'credit_amount', 
    'running_balance_amount', 
    'extended_text', 
    'bank_reference_number' 
]
CONFIG['atbimp']['create_table_import'] = """
CREATE TABLE import (
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
