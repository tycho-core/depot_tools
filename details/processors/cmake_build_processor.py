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
        self.__inputs = []

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
    	bindings = package_set.get_package_bindings()
    	for bound_pkg in bindings:
    		pkg = bound_pkg.get_package()
    		info = pkg.get_package_info(False)
    		cmake = info.get_build_system('cmake')
    		if cmake:
    			for key, val in six.iteritems(cmake):
    				if key == 'inputs':    					
    					for item in val:
    						# build the relative path to this cmake file
    						rel_path = mappings.apply_templates(
    										os.path.join(bound_pkg.get_package_root_dir(), item)) 
    						print(rel_path)
    						rel_path = CMakeBuildProcessor.__make_cmake_path(rel_path, 
    							workspace.get_root_dir())
    						print(rel_path)
    						self.__inputs.append(rel_path)
    				elif key == 'includes':
    					for item in val:    						
    						rel_path = CMakeBuildProcessor.__make_cmake_path(mappings.apply_templates(item),
    							workspace.get_root_dir())
    						self.__includes.append(rel_path)


    def generate_cmake_file_text(self):
    	""" 
    	Generates a string of the CMakeLists.txt file contents
    	"""
    	contents = ""
    	contents += "cmake_minimum_required (VERSION 2.8)\n\n"
    	for file in self.__inputs:
    		contents += "include(\"%s\")\n" % file

    	contents += "\n"
    	for include in self.__includes:
    		contents += "# " + include + "\n"

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
