import re
from cement import Controller, ex

@ex(help='Display and fix duplicates')
class Duplicates(Controller):
    '''
    Class Duplicates(Controller): controller to handle duplicates found after cvs import 
    commands.  
    
    Accesed by: atbimp dup <command>

    Parameters: None
    '''
    class Meta:
        label = 'duplicates'
        aliases= ['dup']
        help = '''  
                Commands for working with duplicates found after a successfull 
                imported by the 'csv import' command.
            '''
        stacked_type = 'nested'
        stacked_on = 'base'

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        
    ## ====================================================================
    ## Helper Functions
    ##
    @ex(hide=True)
    def _find_duplicate_entries(self, duplicate):
        qry = {
            'query':    '*', 
            'from':     'list_dup_entries', 
            'where':    f"duplicate_id = {duplicate['id']}"
        }
        try:
            dupEntries = self.app.sqlite3.select(qry)
        except:
            raise ConnectionError
        
        return dupEntries
        
    @ex(hide=True)
    def _validate_id(self,id):
        id=id.lower()
        if not re.fullmatch(r'\d*', id):
            # No digit, maybe the workd all
            if not (len(id) and type(id) == str and id =="all"):
                self.app.log.error('  Invalid id spec. Use id number as displayed by list in square brackets [id]')
                self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
                return 
        
        return id


    ## ====================================================================
    ## Controller Code
    ##

    # ----------------------------------------------------------------------
    # ls | List: list duplicates found  
    #
    @ex(
            help="list all duplicates found.",
            aliases=['ls']
    )
    def list(self):
        '''
        ls | list   list all duplicates found
        '''
        duplicates = []
        # find the transactions that have duplictes
        try:
            resDuplicates = self.app.sqlite3.select({'query': '*', 'from': 'list_duplicates'})
        except:
            raise ConnectionError
        
        # loop trough the duplicates list to find the entries that where not imported.
        for duplicate in resDuplicates:
            dupEntries = self._find_duplicate_entries(duplicate)
            # We have it all
            duplicates.append({'entry': duplicate, 'duplicates': dupEntries})

        self.app.render({'duplicates': duplicates},'./duplicates/list.jinja2')


    # ----------------------------------------------------------------------
    # sh | show: show one duplicate 
    #
    @ex(
            help="show one duplicate",
            aliases=['sh'],
            arguments=[(['id'],{
                'help': "the source id of the duplicate. (displayed by 'list' in square brackets [id])",
                'action': 'store'
            })]
    )
    def show(self):
        id = self.app.pargs.id
        if not re.fullmatch(r'\d*', id):
            self.app.log.error('  Invalid id spec. Use id number as displayed by list in square brackets [id]')
            self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
            return 

        # find our duplicate
        try:
            duplicate = self.app.sqlite3.select({'query': '*', 'from': 'list_duplicates', 'where': f"id={id}" })
        except:
            raise ConnectionError

        if len(duplicate) != 1:
            # There can be only one
            self.app.log.warning(f'  Duplicate with id: {id} not found')
            self.app.exit_code = self.app.EC_RECORD_NOT_FOUND
            return 
        
        # find the duplicates attached with this
        duplicate = duplicate[0]
        dupEntries = self._find_duplicate_entries(duplicate)

        # Let's build a list of ransaction entries close to this duplicate to 
        # help the user figure out what this duplicate is about.
        #
        qry={
            'query':  '*',
            'from':   'transactions t',
            'where':  f"account_id={duplicate['account_id']} AND date BETWEEN date('{duplicate['date']}','-1 day') AND date('{duplicate['date']}', '+1 day')",
            'clauses': {'order_by': 't.date, t.id desc'}  
        }
        try:
            entries = self.app.sqlite3.select(qry)
        except:
            raise ConnectionError
        
        # Render output
        data = { 
            'duplicate': {'entry': duplicate, 'duplicates': dupEntries }, 
            'entries': entries,
            'highlight': duplicate['transaction_id']
        }
        self.app.render(data, './duplicates/duplicate.jinja2')


    # ----------------------------------------------------------------------
    # del | rm  | delete: a duplicate or all 
    #
    @ex(
            help="delete one or all duplicates",
            aliases=['del', 'rm'],
            arguments=[(['id'],{
                'help': "the id of the duplicate or 'all'. (displayed by 'list' in square brackets [id])",
                'action': 'store'
            })]
    )
    def delete(self):
        id = self._validate_id(self.app.pargs.id)            
        if id == 'all':
            # Remove all duplicates;
            #
            pass
        pass

    # ----------------------------------------------------------------------
    # imp | import: a duplicate or all 
    #
    @ex(
            help="import one or all duplicates",
            label="import",     
            aliases=['imp'],
            arguments=[(['id'],{
                'help': "the id of the duplicate or 'all'. (displayed by 'list' in square brackets [id])",
                'action': 'store'
            })]
    )
    def ximport(self):  # import is not a valid name
        id = self._validate_id(self.app.pargs.id)            
        if id == 'all':
            True
        pass



        
        
        
