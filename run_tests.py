#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Friday, 05 December 2014 12:10:34 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
import sys
import os

#-----------------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------------

TEST_SEARCH_DIRS = [
    'details'
]

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Run all the tests """
    cwd = os.path.dirname((sys.modules['__main__'].__file__))
    test_loader = unittest.defaultTestLoader
    test_runner = unittest.TextTestRunner()

    for path in TEST_SEARCH_DIRS:
        fullpath = os.path.abspath(os.path.join(cwd, path))
        test_suite = test_loader.discover(fullpath)            
        test_runner.run(test_suite)

if __name__ == "__main__":
    main()
