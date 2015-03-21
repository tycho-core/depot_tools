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
from details.utils.misc import dict_or_default, list_or_default
from copy import deepcopy

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class WorkspaceInfo(object):
    """ WorkspaceInfo """

    class PackageBindingInfo(object):
        """ """

        def __init__(self):
            """ Constructor """
    
    def __init__(self, deps=None, workspace_mappings=None, options=None, bindings=None):
        """ Constructor """
        if deps:
            self.__dependencies = deps
        else:
            self.__dependencies = Dependency.create_root()

        self.__workspace_mappings = dict_or_default(workspace_mappings)
        self.__options = dict_or_default(options)
        self.__bindings = list_or_default(bindings)

    def clone(self):
        """ Create a new copy of this object """
        dependencies = deepcopy(self.__dependencies)
        workspace_mappings = deepcopy(self.__workspace_mappings)
        options = deepcopy(self.__options)
        bindings = deepcopy(self.__bindings)
        return WorkspaceInfo(dependencies, workspace_mappings, options, bindings)

    @staticmethod
    def create_from_json_string(in_str):
        """ Create a PackageInfo object from a json string representation """
        data = json.loads(in_str)

        options = None
        deps = None
        bindings = None
        workspace_mappings = None

        if 'dependencies' in data:
            deps = Dependency.create_from_list(data['dependencies']) 
        if 'bindings' in data:
            bindings = data['bindings']
        if 'options' in data:
            options = data['options']
        if 'workspace_mappings' in data:
            workspace_mappings = data['workspace_mappings']

        return WorkspaceInfo(deps, workspace_mappings, options, bindings)

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
        data = {}

        if len(self.__dependencies.children) > 0:
            data['dependencies'] = [
                str(dep) for dep in self.__dependencies.children
            ]

        if len(self.__workspace_mappings):
            data['workspace_mappings'] = self.__workspace_mappings

        if len(self.__options):
            data['options'] = self.__options

        if len(self.__bindings):
            data['bindings'] = self.__bindings
        
        json_data = json.dumps(data, indent=4, separators=(',', ': '))
        json_file.write(json_data)
        json_file.close()

    def get_dependencies(self):
        """ Returns:
            Dependency[] : All dependencies for this package 
        """
        return self.__dependencies

    def add_dependency(self, dep):
        """ Add a depenency to the workspace """
        self.__dependencies.add_child(dep)

    def get_bindings(self):
        """ Returns:
                list(PackageBinding) : List of bindings of projects in to the workspace
        """
    def get_workspace_mappings(self):
        """ Returns:
             string : relative path to map this package into a workspace
        """
        return self.__workspace_mappings

    def has_option(self, option):
        """ Returns if the info provides the specified option """
        return option in self.__options

    def get_option(self, option):
        """ Get a package option by name
            Returns:
                object : corresponding object. up to caller to know what it is or check
        """
        if self.has_option(option):
            return self.__options[option]
        return None

    def set_package_bindings(self, bindings):
        """ Set the package bindings for this workspace 

            Args: 
                bindings(list(dict)) : Array of dictionaries with binding info in. This should 
                                       contain keys for 'project', 'local_dir' and 'status'
        """
        self.__bindings = bindings

    def get_package_bindings(self):
        """ Return the package bindings for this workspace """
        return self.__bindings
        
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
