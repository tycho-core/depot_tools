#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Wednesday, 19 November 2014 09:50:54 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import sys
import os
import details.format as tyformat
import glob
import os.path
from details.workspace import Workspace
from details.utils.misc import get_script_dir
from details.console_app import ConsoleApp, configure_providers

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class FormatApp(object):
    description = 'See ? for documentation'

    def add_command_line_options(self, parser):
        parser.add_argument('--inplace', '-i', action='store_true', 
                            help='Overwrite the input file with the formatted version')
        parser.add_argument('input_file_patterns', action='store', 
                            help='Input filename for file to format', nargs="+")

    def print_error_context(self):
        """ Override to print extra error information when an exception is caught """
        pass

    def app_main(self, context, options):
        configure_providers(context)

        # load the workspace for the depot tools so we can correctly map file paths
        workspace = Workspace(context, os.path.dirname(get_script_dir()))

        # Expand the patterns listed in the input patterns
        # this is not necessary under bash, as bash does globing itself.
        # However under windows command prompt, globing is not done automatically
        # for you, so this will make it behave the same as under bash
        input_files = []
        for input_file_pattern in context.options.input_file_patterns:
            input_files.extend(glob.glob(input_file_pattern))
        
        if len(input_files) > 1 and not context.options.inplace:
            sys.stderr.write("Multiple files cannot be formatted without '--inplace' option")
            sys.exit(1)
        
        for input_file in input_files:
            FormatApp.format_file(context, input_file)

    @staticmethod
    def format_file(context, input_file):
        """ figure out file type """
        file_type = tyformat.Formatter.get_file_type(input_file)

        if file_type == 'c++':
            fmt = tyformat.Formatter(context)
            if context.options.inplace:
                fmt.format_file_inplace(input_file)
            else:
                fmt.format_file_stdout(input_file)          
        else:
            sys.stderr.write("Unknowm file type (%s)" % (os.path.splitext(input_file)[1]))
            sys.exit(1)

def main():
    """ Main script entry point """
    app = ConsoleApp(FormatApp(), os.path.basename(__file__))
    app.app_main()

if __name__ == "__main__":
    main()
