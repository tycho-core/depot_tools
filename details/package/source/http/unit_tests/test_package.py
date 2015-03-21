#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Tuesday, 03 February 2015 11:45:08 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

""" Unit Tests for Package """

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.test_case import TestCase
from details.package.source.http.package import Package
from details.package.source.http.provider import Provider

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class TestPackage(TestCase):
    """ Package test cases """

    def __make_provider(self):
        # valid params
        test_params = {
            'host' : '',
            'anonymous' : False,
        }
        provider = Provider('pkg', self.context, test_params, None)     
        self.assertIsNotNone(provider)
        return provider    
    
    def test_construct(self):
        pkg = Package(self.__make_provider(), 'bob', 'jane')        
        self.assertIsNotNone(pkg)

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
