#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 03:20:47 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import json
import six
from details.templateengine import TemplateEngine
import details.utils.misc as utils
import os
import os.path

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class WorkspaceMapping(object):
    """ This handles mapping packages into the workspace filesystem """
    
    def __init__(self, root_dir):
        """ Constructor """    
        self.__root_dir = utils.ensure_trailing_slash(root_dir)
        self.__template_params = {}
        self.__template_engine = TemplateEngine(None)
        
    def apply_templates(self, path):
        """ Apply templates to the given path and return a absolute path """
        in_str = path
        if not os.path.isabs(path):
            in_str = '%s%s' % (self.__root_dir, path)
        params = self.__flatten_template_params()
        return self.__template_engine.expand_template_string(params, in_str)
        
    def load_templates_from_json_string(self, in_str):
        """ Load list of mapping templates from a json string """
        templates = json.loads(in_str)
        self.load_templates_from_dict(templates)

    def load_templates_from_json_file(self, path):
        """ Load list of mapping templates from a json file """
        try: 
            template_file = open(path, 'r')
            contents = template_file.read()
            self.load_templates_from_json_string(contents)
        finally:
            template_file.close()                

    def load_templates_from_dict(self, templates):
        """ Load list of templates from a python dictionary """
        # add new templates and replace existing ones
        for key, val in six.iteritems(templates):
            self.__template_params[key] = val

            
    def find_file(self, search_dir, search_file, extensions=None):
        """ Search for a file in the mapped directory

        Args:
            dir(string) : Path to search in. This will have mapping applied to it.
            file(string): Name of file to seach for 
            extensions([string]) : Optional list of extensions to match against

        Returns:
            string : Full path to file if found otherwise None.
        """
        mapped_dir = self.apply_templates(search_dir)
        for dirpath, _, filenames in os.walk(mapped_dir):
            for filename in filenames:
                if extensions:
                    name, ext = os.path.splitext(filename)
                    if name == search_file:
                        if ext in extensions:
                            return os.path.join(dirpath, filename)
                else:
                    if filename == search_file:
                        return os.path.join(dirpath, filename)
        return None



    def __flatten_template_params(self):
        """ Returns copy of template params that have been recursively applied to each other"""
        result = {}
        for key, val in six.iteritems(self.__template_params):
            old_val = val
            while True:                
                new_val = self.__template_engine.expand_template_string(self.__template_params, 
                                                                        old_val)
                if new_val == old_val:
                    result[key] = new_val
                    break
                old_val = new_val

        return result

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
