from cement import Controller, ex

@ex(help='Show Accounts imported in database. Add or modify nickname')
class Accounts(Controller):
    '''
    Class Accounts(Controler): controller to handle the nickname of an account
    accesed by: atbimp accounts <command>

    parameters: None
    '''
    class Meta:
        label = 'accounts'
        aliases = ['act']
        help = "Commands for listing imported accounts and change nick name."
        stacked_type = 'nested'
        stacked_on = 'base'
    
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        
    
    ## ====================================================================
    ## Controller Code
    ##

    # ----------------------------------------------------------------------
    # list: list all accounts imported in the database  
    #
    @ex(
            help='list accounts imported in the database',
            aliases=['ls']
    ) 
    def list(self):
        '''
        ls  | list     list accounts imported in the database.
        ''' 
        data = self.app.sqlite3.select('* from account')
        if len(data) == 0:
            self.app.log.warning('  No accounts found in database')
            self.app.exit_code = self.app.EC_ACCOUNT_NOT_FOUND
            return
        
        self.app.render({'accounts': data}, './accounts/list.jinja2')


    @ex(
            help='set/change nickname for given account',
            aliases=['nn'],
            arguments=[
                (['act_id'],{
                    'help':    'account id for setting the nick name',
                    'action':  'store'
                }),
                (['nick_name'],{
                    'help':    'new nick name for given account',
                    'action':  'store'
                })]
    )
    def nick(self):
        '''
        nn | nick   update nickname on given account
        '''        
        acct_id = self.app.pargs.act_id
        nick = self.app.pargs.nick_name
        
        # First lookup the account
        qry=f"* FROM 'account' WHERE id={acct_id}"
        res = self.app.sqlite3.select(qry)
        if len(res) == 0:
            self.app.log.warning(f'  Account: {acct_id} not found in database')
            self.app.exit_code = self.app.EC_ACCOUNT_NOT_FOUND
            return
        
        # update the nick name
        self.app.sqlite3.update(f"'account' SET nick_name='{nick}' WHERE id={acct_id}")
        
        # lookup again and display to user
        res = self.app.sqlite3.select(qry)
        self.app.render({'accounts': res }, './accounts/list.jinja2')
        
        
        

        
        