#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 11:08:22 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.workspace import Workspace
from details.console_app import ConsoleApp
from details.package.provider_query_interface import InteractiveQueryInterface
from details.utils.misc import add_command_line_action

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

class HubApp(object):
    description = "? for documentation"

    def add_command_line_options(self, parser):
        """
        Add all command line arguments to the main parser. 
        """    
        parser.set_defaults(mode='hub')
        subparsers = parser.add_subparsers()
        
        # list action
        cmd_help = 'Display list of all hub projects'
        sb_help = 'Include sandbox libraries in the output'
        parser = add_command_line_action(subparsers, 'list', action_help=cmd_help)
        parser.add_argument('--sandbox', '-r', action='store_true', help=sb_help)

    def print_error_context(self):
        """ Override to print extra error information when an exception is caught """
        pass
        
    def app_main(self, context, options):
        workspace = Workspace(context, context.current_dir)
        query_interface = context.package_manager.get_aggregated_query_interface()
        interactive_interface = InteractiveQueryInterface(query_interface)

        if not query_interface:
            print 'No providers that can be queried'
            return 1
        if options.action == 'list':
            interactive_interface.print_projects(existing_deps=workspace.get_root_dependency())

        return 0

def main():
    """ Main script entry point """
    app = ConsoleApp(HubApp())
    app.app_main()
                

if __name__ == "__main__":
    main()
