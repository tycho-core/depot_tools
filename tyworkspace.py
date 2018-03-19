#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 11:07:22 AM
#-----------------------------------------------------------------------------

"""
Command line tool to manage hub workspaces
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function
from details.workspace import Workspace
from details.console_app import ConsoleApp, configure_providers
import sys
import os.path

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

class WorkspaceApp(object):
    """ Application """
    description = '? for documentation.'

    def __init__(self):
        self.__context = None

    def add_command_line_options(self, parser):
        Workspace.add_command_line_options(parser)

    def get_error_context(self):
        """ Override to print extra error information when an exception is caught """
        if self.__context.current_dependency:
            chain = self.__context.current_dependency.get_dependency_chain()
            chain_len = len(chain)
            cur_dep = 0
            info = ''
            for link in chain:
                info = info + str(link)
                if cur_dep < chain_len -1:
                    info = info + ' -> '
                cur_dep += 1
            return info


    def get_workspace(self, context, options):
        return Workspace(context,
                        context.current_dir,
                        check_valid=options.validate,
                        refresh_dependencies=options.refresh)

    def app_main(self, context, options):
        """ Main entry point """
        self.__context = context
        configure_providers(context)
        if options.action == 'init':
            if not Workspace.create_new_workspace(context, context.current_dir):
                print("Failed to create workspace")
            else:
                workspace = self.get_workspace(context, options)
                workspace.update()
        elif options.action == 'status':
            workspace = self.get_workspace(context, options)
            workspace.status(detailed=options.detailed, raw=options.raw)
        elif options.action == 'show':
            workspace = self.get_workspace(context, options)
            if options.subaction == 'branches':
                workspace.show_branches()
            elif options.subaction == 'imports':
                imports = workspace.get_available_imports()
                if options.machine:
                    json_obj = {
                        'error': '',
                        'imports': imports
                    }
                    context.console.write_line(ConsoleApp.to_json_string(json_obj))
                else:
                    for imp in imports:
                        msg = '%s:%s' % (imp['provider'], imp['name'])
                        if imp['existing']:
                            msg = '* ' + msg
                        context.console.write_line(msg)
        elif options.action == 'verify':
            workspace = self.get_workspace(context, options)
            if workspace.verify():
                print('Workspace is ok')
            else:
                print('Workspace is not ok')
                return ConsoleApp.EXIT_FAILURE
        elif options.action == 'import':
            workspace = self.get_workspace(context, options)

            if options.project is not None:
                provider, project, version = options.project.split(':')
                workspace.import_project_by_name(provider, project, version)
            else:
                workspace.import_project()

            if options.update:
                # need to reload the workspace to pick up the new dependency
                workspace = self.get_workspace(context, options)
                workspace.update(force=False, preview=False)
        else:
            workspace = self.get_workspace(context, options)
        #    elif options.action == 'clean':
        #       workspace.clean()
            if options.action == 'depends':
                if options.machine:
                    json_obj = {
                        'error': '',
                        'info': workspace.get_depends_info()
                    }
                    context.console.write_line(ConsoleApp.to_json_string(json_obj))
                else:
                    workspace.print_depends(refresh=options.refresh)
            elif options.action == 'update':
                workspace.update(options.force, options.preview)
            elif options.action == 'foreach':
                workspace.foreach(options.args)
            elif options.action == 'versions':
                workspace.print_versions()

def main():
    """ Main script entry point """
    app = ConsoleApp(WorkspaceApp(), os.path.basename(__file__))
    app.app_main()

if __name__ == "__main__":
    main()
