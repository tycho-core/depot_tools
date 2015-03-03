#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Wargaming.net
# Created : Monday, 09 February 2015 12:55:41 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.utils.misc import execute
import re
import os

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------


def is_installed():
    """ Checks to see if git is callable with the current environment """
    exitcode, _, _ = execute('git', os.getcwd(), ['--version'], capture=False)
    return exitcode == 0

def has_credential_helper():
    """ If operating over http or https then user needs to input their username 
    and password for each remote git op, this checks to see if they have installed
    a helper to avoid this """
    config = global_git_config()

    if not config:
        return False

    if 'credential.helper' in config:
        return len(config['credential.helper']) > 0

    return False
    
def global_git_config():
    """ Returns a dictionary representing the global git config """
    exitcode, output, _ = execute('git', os.getcwd(), ['config', '--global', '-l'], capture=True)
    if exitcode != 0:
        return None

    # parse output in form key=value
    regex = r'(?P<key>.+)=(?P<value>.+)'    
    result_dict = {}
    for match in re.finditer(regex, output):
        result_dict[match.group('key')] = match.group('value')

    return result_dict

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
