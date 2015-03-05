#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Monday, 02 February 2015 01:25:08 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.scm.modification import Modification as SCMModification
import re

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Modification(SCMModification):
    """ Modification """

    __git_code_to_code_map = {
        ' ' : SCMModification.Code.Unmodified,
        'M' : SCMModification.Code.Modified,
        'A' : SCMModification.Code.Added,
        'D' : SCMModification.Code.Deleted,
        'R' : SCMModification.Code.Renamed,
        'C' : SCMModification.Code.Copied,
        'U' : SCMModification.Code.UpdatedButUnmerged,
        '?' : SCMModification.Code.Untracked,
        '!' : SCMModification.Code.Ignored
    }

    __code_to_git_code_map = {
        SCMModification.Code.Unmodified : ' ',
        SCMModification.Code.Modified :  'M',
        SCMModification.Code.Added : 'A',
        SCMModification.Code.Deleted : 'D',
        SCMModification.Code.Renamed : 'R',
        SCMModification.Code.Copied : 'C',
        SCMModification.Code.UpdatedButUnmerged : 'U',
        SCMModification.Code.Untracked : '?',
        SCMModification.Code.Ignored : '!'
    }


    @staticmethod
    def code_from_character(char):
        """ Returns:
            Modification.Code : Code corresponding to character as corresponding 
                                http://git-scm.com/docs/git-status
        """
        return Modification.Code(Modification.__git_code_to_code_map[char])
    
    @staticmethod
    def git_code(code):
        """ Returns the git single character code for the code """
        return Modification.__code_to_git_code_map[code]

    __git_status_regex = r'(?P<index>[ MADRCU?!])(?P<local>[ MADRCU?!]) (?P<path>.+)'

    def __init__(self, path, index_code, working_copy_code):
        """ Constructor """
        super(Modification, self).__init__(path, working_copy_code)

        # git reports status on index as well as working copy
        self.__index_code = index_code

    def index_code(self):
        """ Modification code for the index"""
        return self.__index_code


    def __repr__(self):
        return '%s%s %s' % (Modification.git_code(self.__index_code), 
                            Modification.git_code(self.__working_copy_code), 
                            self.__path)
            
    def __eq__(self, other):
        if not other:
            return False

        if type(other) is not Modification:
            return False
        
        return ((self.__path == other.path()) and 
                (self.__index_code == other.index_code()) and 
                (self.__working_copy_code == other.working_copy_code()))
        

    def __neq__(self, other):
        return not self == other

    @staticmethod
    def create_from_git_status_line(in_str):
        """ Create from the output of a single line from git status --porcelain """
        match = re.match(Modification.__git_status_regex, in_str)
        if not match:
            return None

        index_code = Modification.code_from_character(match.group('index'))
        wc_code = Modification.code_from_character(match.group('local'))
        path = match.group('path')

        return Modification(path, index_code, wc_code)

    @staticmethod
    def create_list_from_git_status(text):
        """ Create a list from the output of git status --porcelain """
        result = []
        lines = text.strip().splitlines()
        for line in lines:
            mod = Modification.create_from_git_status_line(line)
            result.append(mod)
        return result

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
