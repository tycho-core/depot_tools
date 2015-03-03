#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 11:12:57 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.package.package_manager import PackageManager
from details.context import Context
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class TestPackageManager(TestCase):
    def test_construct(self):
        ctx = Context()
        PackageManager(ctx, [])        

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
