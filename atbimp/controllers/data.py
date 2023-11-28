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
    def _render_transactions(self, qry, account, options, template):
        # launch our query
        try:
            entries = self.app.sqlite3.select(qry)
        except:
            raise ConnectionError
        
        # Do we need to calculate delta?
        if options['delta']:
            delta = 0
            for (i, entry) in enumerate(entries):
                if i == 0:
                    # first one
                    prevBal = entry['balance']
                    delta = 0.00
                else:
                    # subsequent ones
                    factor = 1 if entry['dc'] == 'C' else -1
                    calcBal = prevBal + (entry['amount'] * factor)
                    delta = entry['balance'] - calcBal
                    prevBal = entry['balance']

                entries[i]['delta'] = delta

        # Calculate the totals
        #
        # start  and end balance
        factor = 1 if entries[0]['dc'] == 'C' else -1
        startBal = entries[0]['balance'] - (entries[0]['amount'] * factor)
        endBal = entries[len(entries)-1]['balance']

        # Calculate debit/credit totals
        debit = 0; credit = 0;
        for entry in entries:
            if entry['dc'] == 'D':
                debit += entry['amount']
            else:
                credit += entry['amount']

        totals = { 
            'start': startBal, 
            'end': endBal,
            'debit': debit,
            'credit': credit 
        }

        # display the result
        self.app.render({
            'entries': entries, 
            'account': account, 
            'options': options,
            'totals' : totals
        },template)

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
                'help':   'show data for month: YYYY-MM (example: -m 2022-04)',
                'action': 'store',
                'dest':   'month'
            }),
            (['-r'],{
                'help':   'show date range: <from>:<to> (example: -r 2022-01-01:2022-03-31)',
                'action': 'store',
                'dest':   'range'  # range is reserved keyword
            }),
            (['-d'],{
                'help':   'show transactions on date: YYYY-MM-DD (example: -r 2022-01-01:2022-03-31)',
                'action': 'store',
                'dest':   'date'
            }),
            (['-a'],{
                'help':   'select account: <alias>|<acct_number>|<nick_name>  (example: -a 1234)',
                'action': 'store',
                'dest':   'account'
            }),
            (['-bw'],{
                'help':   '(b/w): display without color, usefull for printing. [default: Color]',
                'action': 'store_false',
                'dest':   'color'
            }),
            (['-nb'],{
                'help':   'display without box bars. [default: box bars]',
                'action': 'store_false',
                'dest':   'bars'
            }),
            (['-D'],{
                'help':   'calculate and display Delta of running balance. [default Off]',
                'action': 'store_true',
                'dest':   'delta'
            })]
    )
    def show(self):
        '''
        sh | show   month|range
        '''
        options = {
            'color':    self.app.pargs.color,
            'bars':     self.app.pargs.bars,
            'month':    self.app.pargs.month,
            'date':     self.app.pargs.date,
            'rnge':     self.app.pargs.range,        # range is reserved keyword. Will fail in template
            'delta':    self.app.pargs.delta,
            'account':  self.app.pargs.account
        }
        colorMap = self.app.config.get(self.app.label,'colormap')
        options.update({'colorMap': colorMap[options['color']]})
        

        # sanity checks
        if options['month']:
            if not re.fullmatch(r'\d{4}-\d{2}', options['month']):
                self.app.log.error(' Invalid month spec. Use: YYYY-MM')
                self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
                return 
        elif options['rnge']:
            rng = rng=re.fullmatch(r'(?P<from>\d{4}-\d{2}-\d{2}):(?P<to>\d{4}-\d{2}-\d{2})', options['rnge'] )
            if not rng:
                self.app.log.error(' Invalid range spec. Use <from>:<to> YYYY-MM-DD:YYYY-MM-DD')
                self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
                return 
        elif options['date']:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', options['date']):
                self.app.log.error(' Invalid date spec. Use: YYYY-MM-DD')
                self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
                return 

        # get the contents of the accounts table.  We need this later
        #
        accounts = self.app.sqlite3.select({'query': '*', 'from': 'account'})

        prefix = ""
        where = ""
        if options['account']:
            # Lookup our account id
            qry={
                'query': '*',
                'from':  'account',
                'where': f"alias='%{options['account']}%' OR acct_number LIKE '%{options['account']}%' OR nick_name LIKE '%{options['account']}%';"
            }
            res = self.app.sqlite3.select(qry)
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
        if options['account']:
            prefix = " AND "

        if options['month']:
            # Use the month table to speedup queries.
            # isn't that where we designed it for?
            monQry={
                'query': 'id',
                'from':  'month m',
                'where': f"m.month='{options['month']}'"
            }
            res = self.app.sqlite3.select(monQry)
            if len(res):
                # We only want the first one
                where += f"{prefix}month_id={res[0]['id']}"
                prefix = " AND "
                
        elif options['rnge']:
            where += f"{prefix}date BETWEEN '{rng.group('from')}' AND '{rng.group('to')}'"
            prefix = " AND "
            
        elif options['date']:
            where += f"{prefix}date = '{options['date']}'"

        qry.update({'where': where})
        
        # We could be requested to display results over multiple accounts. 
        # but we want to render the result seperately
        if options['account']:
            # Account was specified, just go for it.
            self._render_transactions(qry, accounts[acct_id-1], options, './data/entries.jinja2')
        else:
            # Now we have to figure out wich accounts we will get 
            # back from our query
            where = qry['where']
            acctQry = {
                'query': 'DISTINCT account_id',
                'from':  'transaction',
                'where':  where
            }
            res = self.app.sqlite3.select(acctQry)
            
            # BUG:  Crashes on empty database.
            for acct in res:
                if len(where):
                    prefix = " AND "
                acct_id=acct['account_id']
                qry.update({'where': f"account_id={acct_id}{prefix}{where}"})
                self._render_transactions(qry, accounts[acct_id-1], options, './data/entries.jinja2')



    @ex(
        help='locate an amount in entries',
        aliases=['loc'],
        arguments=[
            # (['-in'],{
            #     'help': 'field to locate: amt (amount) or desc (description) default: amt',
            #     'action': 'store',
            #     'choices': ['amt', 'desc']
            # }),
            (['-a'],{
                'help':   'select account: <alias>|<acct_number>|<nick_name>  (example: -a 1234)',
                'action': 'store',
                'dest':   'account'
            }),
            (['-bw'],{
                'help':   '(b/w): display without color, usefull for printing. [default: Color]',
                'action': 'store_false',
                'dest':   'color'
            }),
            (['-D'],{
                'help':   'calculate and display Delta of running balance. [default Off]',
                'action': 'store_true',
                'dest':   'delta'
            }),
            (['item'],{
                'help': '{amount|text} locates amount in transactions or text in description"',
                'action': 'store'
            })]

    )
    def locate(self):
        '''
        loc | locate  entry in amount or description
        '''
        # FIXME:  Not a lot `DRY` programming between show and locate.
        #
        options = {
            'color':    self.app.pargs.color,
            'bars':     False,
            'delta':    self.app.pargs.delta,
            'account':  self.app.pargs.account
        }
        colorMap = self.app.config.get(self.app.label,'colormap')
        options.update({'colorMap': colorMap[options['color']]})


        # get the contents of the accounts table.  We need this later
        #
        accounts = self.app.sqlite3.select({'query': '*', 'from': 'account'})

        qry = {
            'query':    '*',
            'from':     'transaction'
        }

        # The type will help us with the where clause
        try:
            item = float(self.app.pargs.item)
            where = f"amount={item}"
        except:
            item = self.app.pargs.item
            where = f"description like '%{item}%'"

        if options['account']:
            where += " AND "
            # Lookup our account id
            qry={
                'query': '*',
                'from':  'account',
                'where': f"alias='%{options['account']}%' OR acct_number LIKE '%{options['account']}%' OR nick_name LIKE '%{options['account']}%';"
            }
            res = self.app.sqlite3.select(qry)
            if len(res) != 1:
                # There can be ony one!
                self.app.log.error(' Invalid account specication or account not found. Use <alias>|<acct_number>|<nick_name>')
                self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
                return 

            # Now we have our id, let's start building up the where clause
            acct_id=res[0]['id']
            where = f"account_id = {acct_id}"

        qry.update({'where': where})
        
        # We could be requested to display results over multiple accounts. 
        # but we want to render the result seperately
        if options['account']:
            # Account was specified, just go for it.
            self._render_transactions(qry, accounts[acct_id-1], options, './data/entries.jinja2')
        else:
            # Now we have to figure out wich accounts we will get 
            # back from our query
            where = qry['where']
            acctQry = {
                'query': 'DISTINCT account_id',
                'from':  'transaction',
                'where':  where
            }
            res = self.app.sqlite3.select(acctQry)
            
            # BUG:  Crashes on empty database.
            for acct in res:
                if len(where):
                    prefix = " AND "
                acct_id=acct['account_id']
                qry.update({'where': f"account_id={acct_id}{prefix}{where}"})
                self._render_transactions(qry, accounts[acct_id-1], options, './data/entries.jinja2')


        

