#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Wargaming.net
# Created : Thursday, 05 February 2015 12:34:16 PM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

""" Unit Tests for WorkspaceInfo """

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.test_case import TestCase
from details.workspace_info import WorkspaceInfo

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class TestWorkspaceInfo(TestCase):
    """ WorkspaceInfo test cases """
    
    def test_construct(self):
        info = WorkspaceInfo()        
        self.assertIsNotNone(info)

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
