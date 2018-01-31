#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 05 February 2015 11:36:25 PM
#-----------------------------------------------------------------------------
#pylint: disable=W0703

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function
import sys
import argparse
import os.path
import json
from details.context import Context
from details.utils.misc import vlog, enable_verbose_log

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class ConsoleApp(object):
    """ ConsoleApp """

    @staticmethod
    def to_json_string(obj):
        """ Create a formatted json string from the passed object """
        return json.dumps(obj, indent=4, separators=(',', ': '))

    def __init__(self, app, app_name):
        """ Constructor """
        self.app = app

        # setup main context
        self.context = Context()
        self.description = app.description

        # setup command line args
        self.parser = argparse.ArgumentParser(prog=app_name)
        self.parser.add_argument('--verbose', '-v', 
                                 action='store_true', 
                                 help='Enable verbose logging')

        self.parser.add_argument('--debug', '-d',
                                 action='store_true',
                                 help='Enable debugging support')

        self.parser.add_argument('--noanim', '-n',
                                 action='store_true',
                                 help='Disable console animations')

        self.parser.add_argument('--machine', '-m',
                                 action='store_true',
                                 help='We are being called by another program, output will be to stdout in json format.')

        self.parser.add_argument('--quiet', '-q',
                                 action='store_true',
                                 help='Supress informational messages from being displayed')

        app.add_command_line_options(self.parser)
        self.parser.description = self.description
        self.options = self.parser.parse_args()
        self.context.options = self.options

        if self.options.debug:
            self.options.noanim = True

        if self.options.machine:
            self.options.noanim = True
            self.options.quiet = True

        if self.options.noanim:
            self.context.console.disable_animations()

        if self.options.quiet:
            self.context.console.disable_task_info()

        if self.options.verbose:
            self.context.verbose = True
            enable_verbose_log()
            vlog(self.options)

    def app_main(self):
        """ Main entry point for the application """
        return_code = 1
        if self.options.debug:
            return_code = self.__app_main_aux()
        else:
            try:
                return_code = self.__app_main_aux()
            except Exception as ex:
                # ensure the console writer is shutdown and threads stopped
                self.context.console.shutdown()

                # print exception and user data
                msg = str(ex)
                extra = self.app.get_error_context()
                if extra:
                    msg = msg + ' : ' + extra
                if self.options.machine:
                    print(ConsoleApp.to_json_string({
                        "error": msg
                    }))
                else:
                    print(msg)
                sys.exit(1)

        self.context.console.shutdown()
        sys.exit(return_code)

    def __app_main_aux(self):
        """ Main entry point for the application """
        return self.app.app_main(self.context, self.options)

def configure_providers(context):
    from details.package.package_manager import PackageManager

    # configure providers
    context.console.start_task('Configuring providers')
    provider_file = open(os.path.join(context.config_dir, 'hub-providers.json'), 'r')
    providers = json.load(provider_file)
    provider_file.close()
    context.package_manager = PackageManager(context, providers)
    context.console.end_task()

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
