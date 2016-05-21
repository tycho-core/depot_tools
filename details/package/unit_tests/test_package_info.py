#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 11:42:07 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

""" Unit Tests for PackageInfo """

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
import textwrap
from details.test_case import TestCase
from details.package.package_info import PackageInfo
from details.depends import Dependency

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class TestPackageInfo(TestCase):
    """ PackageInfo test cases """

    __test_data = """
    {
        "workspace_mapping" : "./foo",
        "dependencies" : [
            "hub:core:v1",
            "sandbox:build:v2"            
        ],
        "build" : {
            "cmake" : {
                "file" : "CMakeLists.txt"
            }
        }
    }
    """
    
    def test_construct(self):
        pkg = PackageInfo()        
        self.assertIsNotNone(pkg)
        self.assertEquals(len(pkg.get_dependencies().children), 0)
        self.assertEquals(pkg.get_workspace_mapping(), '')

        deps = Dependency.create_root()
        deps.add_child(Dependency.create_root())
        pkg = PackageInfo(deps=deps, workspace_mapping='./foo', options=None, build={'cmake' : {}})
        self.assertEquals(len(pkg.get_dependencies().children), 1)
        self.assertEquals(pkg.get_workspace_mapping(), './foo')
        self.assertIsNotNone(pkg.get_build_system('cmake'))


    def __check_test_info(self, pkg):
        self.assertIsNotNone(pkg)
        deps = pkg.get_dependencies()
        self.assertIsNotNone(deps)
        self.assertEquals(len(deps.children), 2)
        self.assertEquals(deps.children[0].source, 'hub')
        self.assertEquals(deps.children[0].name, 'core')
        self.assertEquals(deps.children[0].branch, 'v1')
        self.assertEquals(deps.children[1].source, 'sandbox')
        self.assertEquals(deps.children[1].name, 'build')
        self.assertEquals(deps.children[1].branch, 'v2')
        self.assertIsNotNone(pkg.get_build_system('cmake'))

    def test_create_from_json_file(self):
        pass

    def test_create_from_json_string(self):
        pkg = PackageInfo.create_from_json_string(textwrap.dedent(TestPackageInfo.__test_data))
        self.__check_test_info(pkg)


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
