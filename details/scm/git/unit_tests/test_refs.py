#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 09:00:10 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
import textwrap
from details.scm.git.refs import Refs
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Unit Tests
#-----------------------------------------------------------------------------

class TestGitRefs(TestCase):
    def test_construct(self):
        return Refs([])

    def test_create_from_string(self):
        test_data = """
            2cfbc70d3640e3d558f5ea5f66efce65ddd95d45        HEAD
            625e964f1f0c9a95e8ecdfc9687a4d84dbf38d6f        refs/heads/branch
            2cfbc70d3640e3d558f5ea5f66efce65ddd95d45        refs/heads/master
        """
        refs = Refs.create_from_string(textwrap.dedent(test_data))
        self.assertEqual(refs.num_refs(), 3)

        ref = refs.find_reference('HEAD')
        self.assertIsNotNone(ref)
        self.assertEqual(ref.sha, '2cfbc70d3640e3d558f5ea5f66efce65ddd95d45')
        self.assertTrue(ref.refers_to('HEAD'))


        ref = refs.find_reference('branch')
        self.assertIsNotNone(ref)
        self.assertEqual(ref.sha, '625e964f1f0c9a95e8ecdfc9687a4d84dbf38d6f')
        self.assertTrue(ref.refers_to('branch'))

        ref = refs.find_reference('master')
        self.assertIsNotNone(ref)
        self.assertEqual(ref.sha, '2cfbc70d3640e3d558f5ea5f66efce65ddd95d45')
        self.assertTrue(ref.refers_to('master'))


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
