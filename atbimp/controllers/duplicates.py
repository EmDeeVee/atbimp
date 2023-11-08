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
            'from':     'list_duplicate_entry', 
            'where':    f"duplicate_id = {duplicate['id']}"
        }
        dupEntries = self.app.sqlite3.select(qry)
        return dupEntries
        
    @ex(hide=True)
    def _validate_id(self,id):
        if type(id) == str:
            id=id.lower()
        else:
            id=str(id)

        if not (re.fullmatch(r'\d*', id) and id != '0'):
            # No digit, maybe the word all
            if not (len(id) and id == "all"):
                return ''
        
        return str(id)
    
    @ex(hide=True)
    def _get_confirmation(self, prompt):
        response = input(prompt).upper()
        cont=False
        if response == 'Y' or response == "YES":
            cont = True

        return cont

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
        resDuplicates = self.app.sqlite3.select({'query': '*', 'from': 'list_duplicate'})
        
        # loop trough the duplicates list to find the entries that where not imported.
        if len(resDuplicates):
            for duplicate in resDuplicates:
                dupEntries = self._find_duplicate_entries(duplicate)
                # We have it all
                duplicates.append({'entry': duplicate, 'duplicates': dupEntries})

            self.app.render({'duplicates': duplicates},'./duplicates/list.jinja2')
        else:
            self.app.log.info('No duplicates found.')


    # ----------------------------------------------------------------------
    # sh | show: show one duplicate 
    #
    @ex(
            help="show one duplicate",
            aliases=['sh'],
            arguments=[(['src_id'],{
                'help': "the source id of the duplicate. (displayed by 'list' in square brackets [src_id])",
                'action': 'store',
                # 'dest': 'id'
            })]
    )
    def show(self,id=None, dup2highlight=None):
        if not id:
            id = self._validate_id(self.app.pargs.src_id)

        if len(id)==0:
            self.app.log.error('  Invalid id spec. Use duplicate source id as displayed by list in square brackets [id]')
            self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
            return 
        
        if id == 'all':
            # that is the list statement.
            self.list()
            return

        # find our duplicate
        duplicate = self.app.sqlite3.select({'query': '*', 'from': 'list_duplicate', 'where': f"id={id}" })

        if len(duplicate) != 1:
            # There can be only one
            self.app.log.warning(f'  Duplicate with source id: [{id}] not found')
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
            'from':   'transaction t',
            'where':  f"account_id={duplicate['account_id']} AND date BETWEEN date('{duplicate['date']}','-1 day') AND date('{duplicate['date']}', '+1 day')",
            'clauses': {'order_by': 't.date, t.id desc'}  
        }
        entries = self.app.sqlite3.select(qry)

        # Render output
        data = { 
            'duplicate': {'entry': duplicate, 'duplicates': dupEntries }, 
            'entries': entries,
            'highlight': {
                'transaction': duplicate['transaction_id'],
                'duplicate':   dup2highlight
            }
        }
        self.app.render(data, './duplicates/duplicate.jinja2')


    # ----------------------------------------------------------------------
    # del | rm  | delete: a duplicate or all 
    #
    @ex(
            help="delete one or all duplicates",
            aliases=['del', 'rm'],
            arguments=[(['dup_id'],{
                'help': "the id of the duplicate or 'all'. (displayed by 'list' in round brackets (dup_id))",
                'action': 'store'
            }),(['-y', '--yes'],{
                'help':     "Don't ask for confirmation.",
                'action':   'store_false',
                'dest':     'confirm',
                'default':  True
            }),(['-b', '--brief'],{
                'help':     "brief.  Don't show what will be deleted. (ignored when using --yes)",
                'action':   'store_true',
                'default':  False
            })] 
    )
    def delete(self):
        confirm = self.app.pargs.confirm
        brief = self.app.pargs.brief           
        dup_id = self._validate_id(self.app.pargs.dup_id)
        if len(dup_id) == 0 or dup_id == '0':
            # We did not pass the test
            self.app.log.error('  Invalid id spec. Use duplicate id as displayed by list in round brackets (id)')
            self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
            return 

        elif dup_id == 'all':
            # Remove all duplicates;
            # easy
            # Show what will be deleted
            cont = True
            if confirm:
                if not brief:
                    self.list()
                cont = self._get_confirmation("Do you want to delete ALL duplicates? [y/N]")

            if not cont:
                self.app.exit_code = self.app.EC_CONFIRMATION_CANCEL
                return 0        # number of rows affected
            
            # We're good.  Delete them all
            rowsAffected =  self.app.sqlite3.delete('FROM duplicate')
            rowsAffected += self.app.sqlite3.delete('FROM duplicate_entry')

        else: 
            # Figure out what to delete
            qry={'query': 'duplicate_id', 'from': 'duplicate_entry', 'where': f'id={dup_id}'}
            res = self.app.sqlite3.select(qry)
            
            if len(res) != 1:
                # There can be only one
                self.app.log.warning(f'  Duplicate with duplicate id: ({dup_id}) not found')
                self.app.exit_code = self.app.EC_RECORD_NOT_FOUND
                return 
            
            src_id=str(res[0]['duplicate_id'])
            cont = True
            if confirm:
                if not brief:
                    self.show(src_id, dup_id)
                cont = self._get_confirmation(f"Do you want to delete duplicate ({dup_id})? [y/N]")
                

            if not cont:
                self.app.exit_code = self.app.EC_CONFIRMATION_CANCEL
                return 0        # number of rows affected
            
            # We're good. Delete the single duplicate
            self.app.sqlite3.delete(
                {'from' : 'duplicate_entry', 
                 'where': f'id={dup_id}'
            })

            # Check to see if we also need to delete the parent `duplicate'
            res = self.app.sqlite3.select(
                {'query': 'id', 
                 'from' : 'duplicate_entry', 
                 'where': f'duplicate_id={src_id}'})
            if len(res) == 0:
                # yes we also need to delete the parent
                self.app.sqlite3.delete(
                    {'from' : 'duplicate',
                     'where': f'id={src_id}'}
                )


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
        else:
            self.app.exit_code = self.app.EC_PARAM_WRONG_FORMAT
            return

        pass



        
        
        
