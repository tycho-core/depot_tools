#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Tuesday, 03 February 2015 11:45:34 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

""" Unit Tests for Provider """

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.test_case import TestCase
from details.package.source.http.provider import Provider

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class TestProvider(TestCase):
    """ Provider test cases """

    __test_host = 'http://martins-pc.bigworldtech.com/'    
    
    def __make_provider(self):
        # valid params
        test_params = {
            'host' : TestProvider.__test_host
        }
        provider = Provider('pkg', self.context, test_params, None)     
        self.assertIsNotNone(provider)
        return provider

    def test_construct(self):
        self.__make_provider()

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
