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
                (['import_id'],{
                'help':   'import id to show',
                'action': 'store',
                'default': 'all'
            })]
    )
    def show(self, id=None):
        if not id:
            import_id = self.app.pargs.import_id

        if import_id == 'all':
            # that's the list
            self.list()
            return
        
        # Get the data sets, first import
        res = self.app.sqlite3.select({
            'query':    "id, time_stamp, source",
            'from':     'import',
            'where':    f"id={import_id}",
        })
        if len(res) == 0:
            print(f'Import id: {import_id} not found')
            return False

        imp = res[0]

        # Get the report
        res = self.app.sqlite3.select({
            'query':    "source as fileChecked, 'n/a' as fileExported, linesRead, dataLinesFound, incorrectDate, leadingQuote, trailingComma, singleQuote, totalErrors, recordsImported, recordsExported, sqlInsertErrors, duplicatesFound",
            'from':     'import',
            'where':    f"id={import_id}",
        })
        report = res[0]

        # get the duplicates
        duplicates = []
        qry = {
            'query':    '*',
            'from':     "transaction",
            'where':    f"import_id = {import_id} AND flag='D'"
        }
        res = self.app.sqlite3.select(qry)
        if len(res):
            # find matching originals
            qry.update({'from': 'transaction t', 'join': 'import i ON i.id = t.import_id'})
            for duplicate in res:
                qry.update({'where': f"t.id={duplicate['duplicate_of']}"})
                res2 = self.app.sqlite3.select(qry)
                original = res2[0]
                duplicates.append({'duplicate': duplicate, 'original': original})
                
                
        

        # Render the results
        #
        self.app.render({
            'import'        : imp,
            'report'        : report,
            'duplicates'    : duplicates
        }, './imports/show.jinja2')