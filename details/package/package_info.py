#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 11:11:01 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import json
from details.depends import Dependency

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class PackageInfo(object):
    """ PackageInfo """
    
    def __init__(self, deps=None, workspace_mapping=None, options=None, build=None):
        """ Constructor """
        if deps:
            self.__dependencies = deps
        else:
            self.__dependencies = Dependency.create_root()

        if workspace_mapping:
            self.__workspace_mapping = workspace_mapping
        else:
            self.__workspace_mapping = ''        

        if options:
            self.__options = options
        else:
            self.__options = {}
            
        if build:
            self.__build = build
        else:
            self.__build = {}

    @staticmethod
    def create_from_json_string(in_str):
        """ Create a PackageInfo object from a json string representation """
        data = json.loads(in_str)
        deps = Dependency.create_from_list(data['dependencies']) 
        options = None
        build = None
        if 'options' in data:
            options = data['options']
        if 'build_system' in data:
            build = data['build_system']

        return PackageInfo(deps, data['workspace_mapping'], options, build)

    @staticmethod
    def create_from_json_file(path):
        """ Create a PackageInfo object from a json file """
        json_file = open(path, 'r')
        contents = json_file.read()
        info = PackageInfo.create_from_json_string(contents)
        json_file.close()    
        return info

    def save_to_json_file(self, path):
        """ Write the package info to a json file """
        json_file = open(path, 'w')
        data = {
            'dependencies' : [
                str(dep) for dep in self.__dependencies.children
            ],
            'workspace_mapping' : self.__workspace_mapping,
            'options' : self.__options,
            'build_system'  : self.__build
        }
        json_data = json.dumps(data, indent=4, separators=(',', ': '))
        json_file.write(json_data)
        json_file.close()

    def get_dependencies(self):
        """ Returns:
            Dependency[] : All dependencies for this package 
        """
        return self.__dependencies

    def get_workspace_mapping(self):
        """
            Returns:
            string : relative path to map this package into a workspace
        """
        return self.__workspace_mapping

    def get_build_system(self, name):
        """
            Returns: 
                dict : dictionary of options for the specified build system
                       of None if it is not present
        """
        if name in self.__build:
            return self.__build[name]

        return None

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
