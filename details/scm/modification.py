#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Wargaming.net
# Created : Sunday, 01 February 2015 11:58:09 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from enum import Enum, unique

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Modification(object):
    """ Represents a modification to a package """

    @unique
    class Code(Enum):
        Untracked = 1
        Ignored = 2
        Unmodified = 3
        Modified = 4
        Added = 5
        Deleted = 6
        Renamed = 7
        Copied = 8
        UpdatedButUnmerged = 9

        def __init__(self, code):
            self.code = code

    
    def __init__(self, path, working_copy_code):
        """ Constructor """
        self.__path = path
        self.__working_copy_code = working_copy_code
            

    __code_pretty_name_map = {
        Code.Unmodified : 'Unmodified File',
        Code.Modified :  'Modified File',
        Code.Added : 'Added File',
        Code.Deleted : 'Deleted File',
        Code.Renamed : 'Renamed File',
        Code.Copied : 'Copied File',
        Code.UpdatedButUnmerged : 'File Needs Merging',
        Code.Untracked : 'Untracked File',
        Code.Ignored : '!'    
    }

    def pretty_code_name(self):
        return Modification.__code_pretty_name_map[self.__working_copy_code]


    def working_copy_code(self):
        """ Modification code for the working copy file  """
        return self.__working_copy_code

    def path(self):
        """ Returns path of modified files """
        return self.__path            

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
