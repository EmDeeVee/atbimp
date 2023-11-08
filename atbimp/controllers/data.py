import re
from cement import Controller,ex

@ex(help='Display and lookup entries from the database')
class Data(Controller):
    '''
    Class Data(Controller): controller to handle the data in the database. 
    Preform display of transactions and/lookup.
    
    Accessed by: atbimp dat <command>

    Parameters: None
    '''
    class Meta:
        label = 'data'
        aliases = ['dat']
        help='''
                Commands for displaying and lookup entries in the datbase that
                where imported by the 'csv import' command
            '''
        stacked_type = 'nested'
        stacked_on = 'base'

    ## ====================================================================
    ## Helper Functions
    ##
    def _render_transactions(self, qry, account, month, range, date):
        # launch our query
        try:
            entries = self.app.sqlite3.select(qry)
        except:
            raise ConnectionError
        
        # display the result
        self.app.render({'entries': entries, 'account': account, 'month': month, 'range': range, 'date': date},'./data/entries.jinja2')

    ## ====================================================================
    ## Controller Code
    ##


    # ----------------------------------------------------------------------
    # show: show transaction entries
    #
    @ex(
        help="show transaction entries.",
        aliases=['sh'],
        arguments=[
            (['-m'],{
                'help': 'show data for month: YYYY-MM (example: -m 2022-04)',
                'action': 'store',
                'dest': 'month'
            }),
            (['-r'],{
                'help': 'show date range: <from>:<to> (example: -r 2022-01-01:2022-03-31)',
                'action': 'store',
                'dest': 'range'
            }),
            (['-d'],{
                'help': 'show transactions on date: YYYY-MM-DD (example: -r 2022-01-01:2022-03-31)',
                'action': 'store',
                'dest': 'date'
            }),
            (['-a'],{
                'help': 'select account: <alias>|<acct_number>|<nick_name>  (example: -a 1234)',
                'action': 'store',
                'dest': 'account'
            })]
    )
    def show(self):
        '''
        sh | show   month|range
        '''
        month = self.app.pargs.month
        range = self.app.pargs.range
        date  = self.app.pargs.date
        if month:
            if not re.fullmatch(r'\d{4}-\d{2}', month):
                self.app.log.error(' Invalid month spec. Use: YYYY-MM')
                self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
                return 
        elif range:
            rng = rng=re.fullmatch(r'(?P<from>\d{4}-\d{2}-\d{2}):(?P<to>\d{4}-\d{2}-\d{2})', range )
            if not rng:
                self.app.log.error(' Invalid range spec. Use <from>:<to> YYYY-MM-DD:YYYY-MM-DD')
                self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
                return 
        elif date:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
                self.app.log.error(' Invalid date spec. Use: YYYY-MM-DD')
                self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
                return 
        # else:
        #     self.app.log.error(' Must specify either -m MONTH or -r RANGE')
        #     self.app.exit_code = self.app.EC_PARAM_MISSING
        #     return 

        account = self.app.pargs.account

        # get the contents of the accounts table.  We need this later
        #
        try:
            accounts = self.app.sqlite3.select({'query': '*', 'from': 'account'})
        except:
            raise ConnectionError

        prefix = ""
        where = ""
        if account:
            # Lookup our account id
            qry={
                'query': '*',
                'from':  'account',
                'where': f"alias='%{account}%' OR acct_number LIKE '%{account}%' OR nick_name LIKE '%{account}%';"
            }
            try:
                res = self.app.sqlite3.select(qry)
            except:
                raise ConnectionError
            if len(res) != 1:
                # There can be ony one!
                self.app.log.error(' Invalid account specication or account not found. Use <alias>|<acct_number>|<nick_name>')
                self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
                return 

            # Now we have our id, let's start building up the where clause
            acct_id=res[0]['id']
            where = f"account_id = {acct_id}"

        qry={
            'query': '*',
            'from': 'transaction t',
            'clauses': {'order_by': 't.date, t.id desc'}
        }
        # Add account number, if any, into the mix
        if account:
            prefix = " AND "

        if month:
            where += f"{prefix}date LIKE '{month}-%'"
        elif range:
            where += f"{prefix}date BETWEEN '{rng.group('from')}' AND '{rng.group('to')}'"
        elif date:
            where += f"{prefix}date = '{date}'"

        qry.update({'where': where})
        # We could be requested to display results over multiple accounts. 
        # but we want to render the result seperately
        if account:
            # Account was specified, just go for it.
            self._render_transactions(qry, accounts[acct_id-1], month, range, date)
        else:
            # Now we have to figure out wich accounts we will get 
            # back from our query
            where = qry['where']
            acctQry = {
                'query': 'DISTINCT account_id',
                'from':  'transaction',
                'where':  where
            }
            try:
                res = self.app.sqlite3.select(acctQry)
            except:
                raise ConnectionError
            
            for acct in res:
                if len(where):
                    prefix = " AND "
                acct_id=acct['account_id']
                qry.update({'where': f"account_id={acct_id}{prefix}{where}"})
                self._render_transactions(qry, accounts[acct_id-1], month, range, date)



    @ex(
        help='locate an amount in entries',
        aliases=['loc'],
        arguments=[
            (['-in'],{
                'help': 'field to locate: amt (amount) or desc (description)',
                'action': 'store',
                'choices': ['amt', 'desc']
            }),
            (['-a'],{
                'help': 'in <account_alias>|<account_number>  (example: -a 1234)',
                'action': 'store',
                'dest': 'account'
            }),
            (['item'],{
                'help': 'item to locate',
                'action': 'store'
            })]

    )
    def locate(self):
        '''
        loc | locate  entry in amount or description
        '''
        pass

