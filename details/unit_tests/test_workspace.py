#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 10:20:28 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.workspace import Workspace
from details.context import Context
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Unit Tests
#-----------------------------------------------------------------------------

class TestWorkspace(TestCase):
    def test_construct(self):
        pass
        #ctx = Context()
        #Workspace(ctx, '/root_dir')

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
