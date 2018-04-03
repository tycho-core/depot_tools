#-----------------------------------------------------------------------------
# Darkstorm Library
# Copyright (C) 2016 Martin Slater
# Created : Saturday, 21 May 2016 01:08:26 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import six
import os.path

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class CMakeBuildProcessor(object):
    """ CMakeBuildProcessor """
    
    def __init__(self, context):
        """ Constructor """
        self.__context = context
        self.__includes = []

    @staticmethod
    def __make_cmake_path(path, root):
        rel_path = os.path.relpath(path, root)
        return rel_path.replace('\\', '/')

    def process(self, workspace, package_set):
        """ 
        Iterate over the given package set and collect cmake build directives

        Args:
            package_set(PackageSet) : Package set to iterate
        """
        mappings = workspace.get_filesystem_mappings()

        # get all mapping directories except the top level tycho dir
        all_dirs = mappings.get_all_directories()
        all_dirs.remove(mappings.apply_templates('@{ty_hub_base}'))
        ws_root = workspace.get_root_dir()
        self.__includes = [ CMakeBuildProcessor.__make_cmake_path(path, ws_root) for path in all_dirs ]


    def generate_cmake_file_text(self):
        """
        Generates a string of the CMakeLists.txt file contents
        """
        contents = ""
        contents += "cmake_minimum_required (VERSION 3.1)\n\n"

        contents += "set(TYCHO_CMAKE_SEARCH_DIRS\n"
        for sdir in self.__includes:
            contents += '\t' + sdir + '\n'
        contents += ")\n"

        return contents

    def write_cmake_file(self, out_path):
        """ Write the cmake contents to a file on disk """
        contents = self.generate_cmake_file_text()
        out_file = open(out_path, 'w+')
        out_file.write(contents)
        out_file.close()



            

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
