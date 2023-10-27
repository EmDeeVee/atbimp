
from cement import Controller, ex
from cement.utils.version import get_version_banner
from ..core.version import get_version

VERSION_BANNER = """
Will allow you to import ATB csv files and list transactions %s
%s
""" % (get_version(), get_version_banner())


class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = '''
    Will allow you to import ATB csv files and list transactions

    1) Check, fix and import your csv files using the 'csv' sub commands'
    2) Optionally you can assign nick-names to the accounts imported using 
       'data accounts' commands.
    3) After import check for duplicates or false positives and decide to 
       import them after all, or mark as duplicate and remove.
    4) display months, date ranges or find a specific amount or part of the
       description using the csv data commands.
'''

        # text displayed at the bottom of --help output
        epilog = ''

        # controller level arguments. ex: 'atbimp --version'
        arguments = [
            ### add a version banner
            ( [ '-v', '--version' ],
              { 'action'  : 'version',
                'version' : VERSION_BANNER } ),
        ]


    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()
        print(self.app.sqlite3.get_dbfile())


    # @ex(
    #     help='example sub command1',

    #     # sub-command level arguments. ex: 'atbimp command1 --foo bar'
    #     arguments=[
    #         ### add a sample foo option under subcommand namespace
    #         ( [ '-f', '--foo' ],
    #           { 'help' : 'notorious foo option',
    #             'action'  : 'store',
    #             'dest' : 'foo' } ),
    #     ],
    # )
    # def command1(self):
    #     """Example sub-command."""

    #     data = {
    #         'foo' : 'bar',
    #     }

    #     ### do something with arguments
    #     if self.app.pargs.foo is not None:
    #         data['foo'] = self.app.pargs.foo

    #     self.app.render(data, 'command1.jinja2')
