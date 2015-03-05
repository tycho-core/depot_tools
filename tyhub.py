#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 11:08:22 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.workspace import Workspace
from details.scm.git.thehub import TheHub
from details.console_app import ConsoleApp

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

class HubApp(object):
    description = "? for documentation"

    def add_command_line_options(self, parser):
        TheHub.add_command_line_options(parser)

    def app_main(self, context, options):
        workspace = Workspace(context, context.current_dir)
        hub = TheHub(workspace=workspace)
        if options.action == 'list':
            hub.show_hub_projects(existing_deps=workspace.get_root_dependency())

def main():
    """ Main script entry point """
    app = ConsoleApp(HubApp())
    app.app_main()
                

if __name__ == "__main__":
    main()
