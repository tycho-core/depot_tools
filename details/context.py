#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 10:32:08 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
import details.utils.misc as utils
import details.utils.file as futils
from details.console_writer import ConsoleWriter

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Context(object):
    def __init__(self):
        self.setup(temp_dir=os.path.abspath(os.path.join(utils.get_script_dir(), '..', 'temp')))

    def setup(self, temp_dir, clean_temp=False):
        """ Configure the context with defaults """
        self.base_dir = utils.get_script_dir()
        self.temp_dir = temp_dir
        self.current_dir = os.getcwd()

        # Path to template directory
        self.template_path = os.path.abspath(os.path.join(self.base_dir, '..', 'templates'))

        # Path to configuration folder
        self.config_dir = os.path.abspath(os.path.join(self.base_dir, '..', 'config'))

        # Path to common template directory
        self.common_template_path = os.path.abspath(os.path.join(self.template_path, 'common'))

        # Per project template directory name
        self.project_template_dir = 'project_templates'

        # Template search directories
        self.common_template_directories = ['cpp', 'python']
        
        # Template search paths
        self.common_template_paths = [
            os.path.abspath(os.path.join(self.common_template_path, tdir)) 
            for tdir in self.common_template_directories
            ]

        # Template description file name
        self.template_info = 'info.json'
        
        # Path to global libary options file
        self.global_options_path = os.path.join(self.template_path, 'global_options.json')

        # Name of project options file
        self.project_options_name = 'project_options.json'
        
        # Path to default workspace layout
        self.workspace_layout_path = os.path.join(self.template_path, 'Workspace')
        
        # Path where libraries are cached when performing dependency checks etc.
        self.library_cache_path = ('%s/libCache') % self.temp_dir
        
        # File name of package info file
        self.package_info_filename = 'typackage.info'
        
        # File name of the workspace info file
        self.workspace_info_filename = 'tyworkspace.info'

        # File name of the local workspace info file
        self.local_workspace_info_filename = 'tyworkspace.info.local'
        
        # File name of the workspace cmake file
        self.local_workspace_cmake_filename = 'tyworkspace.cmake'
        
        # Path to where repositories are cached 
        self.repo_cache_path = ('%s/repo_cache/') % self.temp_dir
        
        # True for detailed logging 
        self.verbose = False
        
        # Command line options we were run with
        self.options = None

        # Mapping to use when mapping packages in to workspace
        self.filesystem_mappings = None

        # Current dependency being processed or none if not in this phase. 
        # This is used for error reporting
        self.current_dependency = None 

        # setup console ouput
        self.console = ConsoleWriter()

        # set to true to prompt user for credentials. 
        self.prompt_credentials = False

        # makes sure temp dir exists
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        if clean_temp:
            contents = futils.get_directory_tree(self.temp_dir)
            if contents:
                contents.delete()

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
