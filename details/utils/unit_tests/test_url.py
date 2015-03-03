#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 09:05:18 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.utils.url import Url
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class TestUrl(TestCase):
    def test_construct(self):
        url = Url()
        self.assertIsNone(url.username)
        self.assertIsNone(url.password)
        self.assertIsNone(url.protocol)
        self.assertIsNone(url.host)
        self.assertIsNone(url.path)

        url = Url('http://www.bob.com')
        self.assertEquals(url.protocol, 'http')
        self.assertEquals(url.host, 'www.bob.com')
        self.assertEquals(url.path, None)
        self.assertEquals(url.username, None)
        self.assertEquals(url.password, None)

        url = Url('http://www.bob.com/')
        self.assertEquals(url.protocol, 'http')
        self.assertEquals(url.host, 'www.bob.com')
        self.assertEquals(url.path, None)
        self.assertEquals(url.username, None)
        self.assertEquals(url.password, None)

        url = Url('https://bob:john@www.bob.com')
        self.assertEquals(url.protocol, 'https')
        self.assertEquals(url.host, 'www.bob.com')
        self.assertEquals(url.username, 'bob')
        self.assertEquals(url.password, 'john')

        url = Url('https://bob:john@www.bob.com/path/to/use')
        self.assertEquals(url.protocol, 'https')
        self.assertEquals(url.host, 'www.bob.com')
        self.assertEquals(url.username, 'bob')
        self.assertEquals(url.password, 'john')
        self.assertEquals(url.path, 'path/to/use')


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
    