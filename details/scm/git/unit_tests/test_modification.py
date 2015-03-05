#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Monday, 02 February 2015 01:25:25 PM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

""" Unit Tests for Modification """

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
import textwrap
from details.test_case import TestCase
from details.scm.git.modification import Modification

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class TestModification(TestCase):
    """ Modification test cases """


    __test_data1 = "AM details/scm/git/modification.py"
    __test_data2 = """
        AM details/scm/git/modification.py
         M details/scm/git/repo.py
        ?? details/scm/git/unit_tests/test_modification.py
    """

    __test_data2_res = [
        Modification('details/scm/git/modification.py', 
                     Modification.Code.Added, Modification.Code.Modified),
        Modification('details/scm/git/repo.py', 
                     Modification.Code.Unmodified, Modification.Code.Modified),
        Modification('details/scm/git/unit_tests/test_modification.py', 
                     Modification.Code.Untracked, Modification.Code.Untracked),
    ]
    
    def test_construct(self):
        mod = Modification('', Modification.Code.Added, Modification.Code.Added)        
        self.assertIsNotNone(mod)
        self.assertEqual(mod, Modification('', Modification.Code.Added, Modification.Code.Added))
        self.assertNotEqual(mod, Modification('', Modification.Code.Added, Modification.Code.Copied))


    def test_create_from_git_status_line(self):
        mod = Modification.create_from_git_status_line(TestModification.__test_data1)
        self.assertIsNotNone(mod)
        self.assertEqual(mod, Modification('details/scm/git/modification.py', 
                                           Modification.Code.Added, 
                                           Modification.Code.Modified))

    def test_create_list_from_git_status(self):
        mods = Modification.create_list_from_git_status(textwrap.dedent(TestModification.__test_data2))
        self.assertIsNotNone(mods)
        self.assertEqual(len(mods), len(TestModification.__test_data2_res))
        for mod, res in zip(mods, TestModification.__test_data2_res):
            self.assertEqual(mod, res)


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
