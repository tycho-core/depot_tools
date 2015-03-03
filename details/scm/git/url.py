#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Wednesday, 03 December 2014 06:00:12 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import re
import urllib

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Url(object):
    """ Simple URL representation """

    def __init__(self, url=None):
        """ Constructor """
        self.username = None
        self.password = None
        self.protocol = None
        self.host = None
        self.path = None

        if url:
            self.__split_url(url)

    def __split_url(self, in_url):
        """ Split the URL into its component parts """
        # <protocol>://<username>:<password>@<host>/<path>
        __url_re = r'(?P<protocol>\w+)://((?P<username>.+):(?P<password>.+)@)?(?P<host>[^/]+)(?:/(?P<path>.*))?'
        match = re.match(__url_re, in_url)
        if not match:
            return None

        self.username = match.group('username')
        self.password = match.group('password')
        self.protocol = match.group('protocol')
        self.host = match.group('host')
        self.path = match.group('path')

        if self.path == '':
            self.path = None
        if self.username == '':
            self.username = None
        if self.password == '':
            self.password = None
        if self.protocol == '':
            self.protocol = 'http'
        if self.host == '':
            self.host = None

    def __repr__(self):
        """
        Returns:
            String representation of the URL 
        """
        path = ''
        user = ''
        proto = ''
        host = ''
        if self.path:
            path = '/' + self.path

        if self.username and self.password:
            user = '%s:%s@' % (self.username, self.password)
        elif self.username:
            user = '%s@' % (self.username)

        if self.protocol:
            proto = '%s://' % (self.protocol)
        if self.host:
            host = self.host

        return '%s%s%s%s' % (proto, user, host, path)

    def needs_credentials(self):
        """
        Returns:
            True If the protocol requires credentials (i.e. is not an ssh connection)
        """
        return self.protocol in ['http', 'https']

    def has_credentials(self):
        """
        Returns:
            True if username and password are present
        """
        return self.username and self.password

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
	pass
