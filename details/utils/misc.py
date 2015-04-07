#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 11:05:37 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import sys
import os
import os.path
import six

if sys.platform in ["win32", "cygwin"]:
    # workaround for http://bugs.python.org/issue17023
    os.environ['PATH'] = os.environ['PATH'].replace('"', '')

    
#-----------------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------------
VERBOSE_LOG = False

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------
            


def enable_verbose_log():
    """ Enable verbose logging, useful for debugging """ 
    global VERBOSE_LOG   
    VERBOSE_LOG = True
    
def indent(num_tabs):
    """ Indent console output """
    for _ in range(num_tabs):
        sys.stdout.write("  ")

def log(msg, tabs=0):
    """ Output log message to stdout """
    indent(tabs)
    print(msg)

def vlog(msg, tabs=0):
    """ Output verbose log message to stdout """
    if VERBOSE_LOG:
        indent(tabs)
        print(msg)

def log_banner(msg):
    log('#-------------------------------------------------------------------------------')
    log('# ' + msg)
    log('#-------------------------------------------------------------------------------')
    
def fatal_error(msg):
    """ Print message and quit """
    print("Error : " + msg)
    sys.exit(1)
    
def get_script_dir():
    """ Get path this script lives in """
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def ensure_valid_pathname(in_str):
    """ Return a filename based on the input string that is safe for use as a directory 
    or filename """
    import base64
    return base64.urlsafe_b64encode(in_str)

def ensure_trailing_slash(in_str, sep=os.path.sep):
    """ ensure there is a trailing slash on the end of the string. Will except unix and windows
        seperators and if one is not present will append os.path.sep"""
    if len(in_str) > 0 and in_str[-1] != '/' and in_str[-1] != '\\':
        in_str += sep
    return in_str             
    
def add_command_line_action(parent_parser, name, action_help, subaction=False):
    """ Add a command line sub parse for and action """
    parser = parent_parser.add_parser(name, help=action_help)
    
    if subaction:
        parser.set_defaults(subaction=name)
    else:
        parser.set_defaults(action=name)        
    return parser
            
def symlink(source, link_name):
    """ Create a simlink to a file. This version works in windows as well """
    os_symlink = getattr(os, "symlink", None)
    if callable(os_symlink):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()            

def execute(executable, root_dir, args, capture=True):
    """ Create a new process and optionally capture its ouput """
    import subprocess

    cmd = [executable]
    cmd.extend(args)
    vlog(cmd)
    vlog(root_dir)
    if capture:
        # there is a problem on OS X with Python 2.7.6 where cwd is not being set correctly in
        # the subprocess.Popen call. Manually change to the correct directory before the call
        # and reset afterwards does work correctly though.
        if root_dir and len(root_dir):
            cur_dir = os.getcwd()
            os.chdir(root_dir)
        process = subprocess.Popen(cmd, 
                                   cwd=root_dir,
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)

        process.wait()
        out = process.stdout.read()
        err = process.stderr.read()
        #vlog('%s\n%s' % (out, err))
        if root_dir and len(root_dir):
            os.chdir(cur_dir)
        if process.returncode == 1:
            log(out)
            log(err)
        return [process.returncode, out, err]
    else:
        process = subprocess.Popen(cmd, cwd=root_dir)
        process.wait()
        return [process.returncode, '', '']


def dict_value_or_none(in_dict, name):
    """ Return value if the key exists or None otherwise """
    if name in in_dict:
        return in_dict[name]
    return None

def dict_or_default(dict):
    """ Returns the passed dictionary if not None or an empty one if it is """
    if dict:
        return dict
    return {}

def list_or_default(list):
    """ Returns the passed list if not None or an empty one if it is """
    if list:
        return list
    return {}

def print_table(rows, delimiters, out_stream):
    if rows == None or len(rows) == 0:
        return

    num_cols = len(rows[0])
    
    # get the maximum width of each of the columns
    column_widths = []
    for col_index in range(num_cols):
        max_width = 0
        for row in rows:
            row_len = len(row[col_index])
            if row_len > max_width:
                max_width = row_len
        column_widths.append(max_width)

    for row in rows:
        for col, max_width, delim in zip(row, column_widths, delimiters):
            out_stream.write(col)
            diff = max_width - len(col)
            out_stream.write(' ' * diff)
            out_stream.write(delim)
        out_stream.write('\n')
                
#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
