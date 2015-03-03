#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 11:13:09 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.package.provider_factory import ProviderFactory
from details.context import Context
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class TestProviderFactory(TestCase):
    def test_construct(self):
        ctx = Context()
        ProviderFactory(ctx)        

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
