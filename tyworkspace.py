#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Wargaming.net
# Created : Thursday, 29 January 2015 11:07:22 AM
#-----------------------------------------------------------------------------

"""
Command line tool to manage hub workspaces
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.workspace import Workspace
from details.console_app import ConsoleApp        

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

class WorkspaceApp(object):
    """ Application """
    description = '? for documentation.'

    def add_command_line_options(self, parser):
        Workspace.add_command_line_options(parser)

    def app_main(self, context, options):
        """ Main entry point """
        if options.action == 'init':
            if not Workspace.create_new_workspace(context, context.current_dir):
                print "Failed to create workspace"
            else:
                workspace = Workspace(context, context.current_dir)
                workspace.update()

        else:
            workspace = Workspace(context, context.current_dir)
            if options.action == 'verify':
                if workspace.verify():
                    print 'Workspace is ok'
                else:
                    print 'Workspace is not ok'
        #    elif options.action == 'clean':
        #       workspace.clean()
            elif options.action == 'status':
                workspace.status(detailed=options.detailed, raw=options.raw)
            elif options.action == 'depends':
                workspace.print_depends(refresh=options.refresh)
            elif options.action == 'update':
                workspace.update(options.force, options.preview)
            elif options.action == 'foreach':           
                workspace.foreach(options.args)
            elif options.action == 'show':
                if options.subaction == 'branches':
                    workspace.show_branches()
            elif options.action == 'import':
                workspace.import_project()
            elif options.action == 'versions':
                workspace.print_versions()

def main():
    """ Main script entry point """
    app = ConsoleApp(WorkspaceApp())
    app.app_main()

if __name__ == "__main__":
    main()
