#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 11:11:29 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.package.package_base import PackageBase
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class MockPackage(PackageBase):

    def __init__(self, provider, pkg_name, pkg_version):
        super(MockPackage, self).__init__(provider, pkg_name, pkg_version)

    def get_package_info(self):
        pass

    def checkout(self, local_dir):
        pass

    def update(self, local_dir):
        pass

    def local_filesystem_status(self, local_dir):
        pass

    def change_version(self, local_dir, force):
        pass


class TestPackage(TestCase):
    def test_construct(self):
        pkg = MockPackage(None, 'bob', 'v2')
        self.assertIsNone(pkg.provider)
        self.assertEquals(pkg.name, 'bob')  
        self.assertEquals(pkg.version, 'v2')

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
