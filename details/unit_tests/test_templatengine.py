#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 10:20:28 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
import textwrap
from details.templateengine import TemplateEngine
from details.context import Context
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Unit Tests
#-----------------------------------------------------------------------------

class TestTemplateEngine(TestCase):
    def test_construct(self):
    	ctx = Context()
        TemplateEngine(ctx)

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
