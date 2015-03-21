#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 11:12:48 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.package.provider_base import ProviderBase
from details.context import Context
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class MockProvider(ProviderBase):
    def __init__(self, context):
        super(MockProvider, self).__init__('brian', context, 'mock', True, None)

    def find_package(self, pkg_name, pkg_version, refresh):
        pass

    def get_package_dependencies(self, package):
        pass

    def get_package_info(self, package):
        pass

class TestProvider(TestCase):
    def test_construct(self):
        ctx = Context()
        mock = MockProvider(ctx)        
        self.assertEquals(mock.versioned, True)
        self.assertEquals(mock.name, 'mock')

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
