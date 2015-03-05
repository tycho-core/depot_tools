#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 05 February 2015 12:34:03 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import json
from details.depends import Dependency

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class WorkspaceInfo(object):
    """ WorkspaceInfo """
    
    def __init__(self, deps=None, workspace_mappings=None, options=None):
        """ Constructor """
        if deps:
            self.__dependencies = deps
        else:
            self.__dependencies = Dependency.create_root()

        if workspace_mappings:
            self.__workspace_mappings = workspace_mappings
        else:
            self.__workspace_mappings = {}      

        if options:
            self.__options = options
        else:
            self.__options = {}
            
    @staticmethod
    def create_from_json_string(in_str):
        """ Create a PackageInfo object from a json string representation """
        data = json.loads(in_str)
        deps = Dependency.create_from_list(data['dependencies']) 
        options = None
        if 'options' in data:
            options = data['options']
        return WorkspaceInfo(deps, data['workspace_mappings'], options)

    @staticmethod
    def create_from_json_file(path):
        """ Create a PackageInfo object from a json file """
        json_file = open(path, 'r')
        contents = json_file.read()
        info = WorkspaceInfo.create_from_json_string(contents)
        json_file.close()    
        return info

    def save_to_json_file(self, path):
        """ Write the package info to a json file """
        json_file = open(path, 'w')
        data = {
            'dependencies' : [
                str(dep) for dep in self.__dependencies.children
            ],
            'workspace_mappings' : self.__workspace_mappings,
            'options' : self.__options
        }
        json_data = json.dumps(data, indent=4, separators=(',', ': '))
        json_file.write(json_data)
        json_file.close()

    def get_dependencies(self):
        """ Returns:
            Dependency[] : All dependencies for this package 
        """
        return self.__dependencies

    def get_workspace_mappings(self):
        """
            Returns:
            string : relative path to map this package into a workspace
        """
        return self.__workspace_mappings

    def has_option(self, option):
        """ Returns if the info provides the specified option """
        return option in self.__options

    def get_option(self, option):
        """
            Get a package option by name
            Returns:
            object : corresponding object. up to caller to know what it is or check
        """
        if self.has_option(option):
            return self.__options[option]
        return None

    def add_option(self, key, value):
        """ Set an option in the info file """
        self.__options[key] = value

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
