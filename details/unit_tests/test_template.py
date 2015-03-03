#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 10:20:28 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.template import Template
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Unit Tests
#-----------------------------------------------------------------------------

class TestTemplate(TestCase):
    def test_construct(self):
        tmp = Template()
        self.assertEqual(tmp.name, '')
        self.assertEqual(tmp.description, '')
        self.assertEqual(tmp.source, '')
        self.assertEqual(len(tmp.options), 0)
        self.assertEqual(len(tmp.excluded_files), 0)

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
