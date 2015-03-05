#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 05 February 2015 11:36:25 PM
#-----------------------------------------------------------------------------
#pylint: disable=W0703

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import sys
import argparse
import os.path
from details.context import Context
from details.utils.misc import vlog, enable_verbose_log

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class ConsoleApp(object):
    """ ConsoleApp """
    
    def __init__(self, app):
        """ Constructor """
        self.app = app

        # setup main context
        self.context = Context()
        self.description = app.description

        # setup command line args
        self.parser = argparse.ArgumentParser(prog=os.path.basename(__file__))
        self.parser.add_argument('--verbose', '-v', 
                                 action='store_true', 
                                 help='Enable verbose logging')

        self.parser.add_argument('--debug', '-d', 
                                 action='store_true', 
                                 help='Enable debugging support')

        app.add_command_line_options(self.parser)
        self.parser.description = self.description
        self.options = self.parser.parse_args()        
        self.context.options = self.options 
        
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
                print ex
                self.app.print_error_context()
        sys.exit(return_code)

    def __app_main_aux(self):
        """ Main entry point for the application """
        return self.app.app_main(self.context, self.options)


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
