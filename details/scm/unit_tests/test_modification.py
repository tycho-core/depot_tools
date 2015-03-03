#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Wargaming.net
# Created : Sunday, 01 February 2015 11:59:02 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

""" Unit Tests for Modification """

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.test_case import TestCase
from details.scm.modification import Modification

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class TestModification(TestCase):
    """ Modification test cases """
    
    def test_construct(self):
        mod = Modification('foo', Modification.Code.Added)        
        self.assertIsNotNone(mod)
        self.assertEqual(mod.path(), 'foo')
        self.assertEqual(mod.working_copy_code(), Modification.Code.Added)

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
