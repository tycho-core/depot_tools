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
import cProfile
import StringIO
import pstats
import signal
from functools import partial
from details.context import Context
from details.utils.misc import vlog, enable_verbose_log

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class ConsoleApp(object):
    """ ConsoleApp """

    EXIT_FAILURE = 1
    EXIT_SUCCESS = 0

    def abort(self):
        """ Abort the running application """
        print('User terminated')
        self.context.console.shutdown()
        sys.exit(1)

    @staticmethod
    def to_json_string(obj):
        """ Create a formatted json string from the passed object """
        return json.dumps(obj, indent=4, separators=(',', ': '))

    def __init__(self, app, app_name):
        """ Constructor """
        self.app = app

        # intercept kill signals from the user and clean nicely
        signal.signal(signal.SIGINT, lambda signal, frame: self.abort());

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

        self.parser.add_argument('--profile', '-p',
                                 action='store_true',
                                 help='Output profiling information to stderr after the command has run')

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
        pr = None
        if self.options.profile:
            pr = cProfile.Profile()
            pr.enable()

        res  = self.app.app_main(self.context, self.options)

        if self.options.profile:
            pr.disable()
            s = StringIO.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            sys.stderr.write(s.getvalue())
            with open('output.cprof', 'wt+') as prof:
                prof.write(s.getvalue());

        return ConsoleApp.EXIT_SUCCESS if res is None else res

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
