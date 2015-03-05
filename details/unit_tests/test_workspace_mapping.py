#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 03:34:30 PM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

""" Unit Tests for WorkspaceMapping """

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
import textwrap
from details.test_case import TestCase
from details.workspace_mapping import WorkspaceMapping

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class TestWorkspaceMapping(TestCase):
    """ WorkspaceMapping test cases """
    
    __test_data = """
        {
            "p1" : "foo",
            "p2" : "bar"
        }
        """

    __test_data2 = """
        {
            "p2" : "banana"
        }
        """

    __test_data3 = """
        {
            "p1" : "foo",
            "p2" : "@{p1}/bar",
            "p3" : "@{p2}"
        }
        """

    def test_construct(self):
        mapping = WorkspaceMapping('/')        
        self.assertIsNotNone(mapping)

    def test_load_from_json_string(self):
        mapping = WorkspaceMapping('/')
        mapping.load_templates_from_json_string(textwrap.dedent(TestWorkspaceMapping.__test_data))

    def test_apply_templates(self):
        mapping = WorkspaceMapping('/')
        mapping.load_templates_from_json_string(textwrap.dedent(TestWorkspaceMapping.__test_data))        
        res = mapping.apply_templates('@{p1}/@{p2}/hello')
        self.assertEquals(res, '/foo/bar/hello')

        # override a template
        mapping.load_templates_from_json_string(textwrap.dedent(TestWorkspaceMapping.__test_data2))        
        res = mapping.apply_templates('@{p1}/@{p2}/hello')
        self.assertEquals(res, '/foo/banana/hello')

    def test_recursive_params(self):
        mapping = WorkspaceMapping('/')
        mapping.load_templates_from_json_string(textwrap.dedent(TestWorkspaceMapping.__test_data3))        
        res = mapping.apply_templates('@{p1}')
        self.assertEquals(res, '/foo')
        res = mapping.apply_templates('@{p2}')
        self.assertEquals(res, '/foo/bar')
        res = mapping.apply_templates('@{p3}')
        self.assertEquals(res, '/foo/bar')




#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
