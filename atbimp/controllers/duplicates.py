from cement import Controller, ex

@ex(help='Display and fix duplicates')
class Duplicates(Controller):
    '''
    Class Duplicates(Controller): controller to handle tuplicates found after cvs import 
    commands.  Aaccesed by atbimp dup <command>

    parameters: None
    '''
    class Meta:
        label = 'duplicates'
        aliases= ['dup']
        help = '''  
                Commands for working with duplicates found after a successfull 
                import by the 'csv imp(ort)' command.
            '''
        stacked_type = 'nested'
        stacked_on = 'base'

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        
    ## ====================================================================
    ## Helper Functions
    ##

    ## ====================================================================
    ## Controller Code
    ##

    # ----------------------------------------------------------------------
    # import: import is a keyword that cannot be used as a method name  
    #
    @ex(
            help="list all duplicates found.",
            aliases=['list']
    )
    def ls(self):
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
            qry = {
                'query':    '*', 
                'from':     'list_dup_entries', 
                'where':    f"duplicate_id = {duplicate['id']}"
            }
            try:
                dupEntries = self.app.sqlite3.select(qry)
            except:
                raise ConnectionError
            
            # We have it all
            duplicates.append({'entry': duplicate, 'duplicates': dupEntries})

        data={}
        data['duplicates'] = duplicates
        self.app.render(data,'./duplicates/list.jinja2')
        print('+++ End of Duplicates report +++' )
            


        
        
        
