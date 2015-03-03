#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Friday, 21 November 2014 08:44:43 AM
#-----------------------------------------------------------------------------
"""
Source code formatting support. This supplies helpers to format source according
to hub conventions.

C++ style is picked to be amenable to formatting with clang-format
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import details.utils.misc as tyutils
import subprocess
import string
import os
import sys

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Formatter(object):
    """ Format files according to the hub standard styles.  """

    __clang_format = [
        ['BasedOnStyle', 'webkit'],
        ['BreakBeforeBraces', 'Allman'],
        ['ColumnLimit', '120'],
        ['TabWidth', '4'],
        ['IndentWidth', '4'],
        ['IndentCaseLabels', 'true'],
        ['AlwaysBreakTemplateDeclarations', 'true'],
        ['AllowShortFunctionsOnASingleLine', 'false']
    ]

    __c_ext = ['.cpp', '.c', '.cxx', '.inl', '.h', '.hpp', '.ipp']

        
    """
    Constructor
    """
    def __init__(self, context):
        self.context = context
        self.tools_dir = os.path.join(tyutils.get_script_dir(), '..' + os.path.sep + 'tools')
        self.tools_dir = os.path.join(self.tools_dir, sys.platform)
        self.clang_path = context.filesystem_mappings.find_file('@{ty_hub_bin_tools}/llvm/bin', 
                                                                'clang-format', ['', '.exe'])

    def __execute_clang(self, input_file, overwrite=False, silent=False):
        """ Execute clang-format to format the file"""

        # build style string
        style_str = '-style="{'
        first = True
        for style in Formatter.__clang_format:
            if not first:
                style_str += ', '
            style_str += '%s: %s' % (style[0], style[1])
            first = False
        
        style_str += '}"'

        # build clang command line
        cmd = [ 
            self.clang_path,
            style_str
        ]

        if overwrite:
            cmd.append('-i')

        cmd.append('"%s"' % input_file)
        cmd_line = string.join(cmd, ' ')
        process = None
        if silent:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(cmd_line, 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       startupinfo=startupinfo)
        else:
            process = subprocess.Popen(cmd_line)
        process.wait()

        if process.returncode == 0:
            return True
        return False



    @staticmethod
    def get_file_type(name):
        """ Figure out file type - only cpp currently """
        ext = os.path.splitext(name)[1]
        if not ext in Formatter.__c_ext:
            return None
        return 'c++'

    def format_file_stdout(self, input_file, silent=False):
        """ Format the file and return a string with formatted contents. """
        return self.__execute_clang(input_file, overwrite=False, silent=silent)
            
    def format_file_inplace(self, input_file, silent=False):
        """ Format the file overwriting the input file"""
        return self.__execute_clang(input_file, overwrite=True, silent=silent)
