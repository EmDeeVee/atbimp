from cement import Controller, ex

@ex(help='Examine and/or roll-back imports from `csv import ...\'')
class Imports(Controller):
    '''
    Class Imports(Controller): controller to handle imports done by
    atbimp csv import ...
    
    parameters: None
    '''
    class Meta:
        label = 'imports'
        aliases=['imp']
        help = 'commands to examine and/or roll-back imports from `csv import ...\''
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
    # list: list all imports 
    #
    @ex(
        help = 'show previous imports',
        aliases=['ls']
    )
    def list(self):
        data = self.app.sqlite3.select('* from import')
        self.app.render({'imports': data }, './imports/list.jinja2')
        
    
    @ex(
        help = 'show details of a specific import',
        aliases = ['sh'],
        arguments=[
                (['id'],{
                'help':   'import id to show',
                'action': 'store',
            })]
    )
    def show(self):
        pass