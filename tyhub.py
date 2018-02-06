#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 11:08:22 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function
from details.workspace import Workspace
from details.console_app import ConsoleApp, configure_providers
from details.package.provider_query_interface import InteractiveQueryInterface
from details.utils.misc import add_command_line_action
from details.utils.file import get_directory_tree
import os.path

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
        nd_help = 'Do not highlight projects that are existing dependencies'
        parser = add_command_line_action(subparsers, 'list', action_help=cmd_help)
        parser.add_argument('--sandbox', '-r', action='store_true', help=sb_help)
        parser.add_argument('--nodeps', '-n', action='store_true', help=nd_help)

        parser = add_command_line_action(subparsers, 'cache', action_help="Perform operations on the package cache")
        parser.add_argument('--update', '-u', action='store_true', help="Update all cached state")
        parser.add_argument('--clear', '-c', action='store_true', help="Delete all cache state")

    def get_error_context(self):
        """ Override to print extra error information when an exception is caught """
        return ""

    def app_main(self, context, options):
        if options.action == 'list':
            configure_providers(context)
            query_interface = context.package_manager.get_aggregated_query_interface()
            interactive_interface = InteractiveQueryInterface(query_interface)

            if not query_interface:
                print('No providers that can be queried')
                return 1
            deps = None
            if not options.nodeps:
                workspace = Workspace(context, context.current_dir, refresh_dependencies=False)
                deps = workspace.get_root_dependency()
            interactive_interface.print_projects(existing_deps=deps)
        elif options.action == 'cache':
            if options.update:
                pass
            elif options.clear:
                context.console.start_task('Deleting cache contents @ ' + context.library_cache_path)
                tree = get_directory_tree(context.library_cache_path)
                tree.delete()
                context.console.end_task()

        return 0

def main():
    """ Main script entry point """
    app = ConsoleApp(HubApp(), os.path.basename(__file__))
    app.app_main()


if __name__ == "__main__":
    main()
