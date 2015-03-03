#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Tuesday, 09 December 2014 03:14:08 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
import os
from details.context import Context

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class TestCase(unittest.TestCase):
    """ Base class of all depot unit tests """
    def setUp(self):
        # override the temporary directory to use
        self.context = Context()
        self.context.setup(
            temp_dir=os.path.join(self.context.temp_dir, 'unit_tests', self.__class__.__name__),
            clean_temp=True)

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
