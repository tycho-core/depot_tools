#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Wednesday, 03 December 2014 05:52:54 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import re
import textwrap

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------


class Refs(object):
    """ Wrapper to help introspecting git refs """

    class Reference(object):
        """ Single git reference """

        def __init__(self, sha, path):
            """ Constructor """
            self.sha = sha
            self.path = path

        def branch_name(self):
            """ branch this reference refers to """
            if len(self.path) == 0:
                return None
            return self.path[-1]

        def refers_to(self, name):
            """ Returns true if this refers to a branch of the passes name """
            branch = self.branch_name()
            if not branch:
                return False
            return branch == name


    class InvalidRef(Exception):
        """ Ref was not in a valid format """
        pass

    @staticmethod
    def create_from_string(in_str):
        """ Pass refs from string. Each ref must be on its own line in the format
            <sha> <path>
        """
        refs = []
        for match in re.finditer(r'(?P<sha>[a-z0-9]+)\s+(?P<path>.+)', in_str):
            if len(match.groups()) != 2:
                raise Refs.InvalidRef()
            sha = match.group('sha')
            full_path = match.group('path')
            path_parts = full_path.split('/')
            refs.append(Refs.Reference(sha, path_parts))

        return Refs(refs)

    def __init__(self, refs):
        """ Constructor """
        self.refs = refs

    def has_branch(self, name):
        """ Returns true if the branch is referred to in the refs """
        for ref in self.refs:
            if ref.refers_to(name):
                return True
        return False


    def num_refs(self):
        """ Returns the number of references we refer to """
        return len(self.refs)

    def find_reference(self, name):
        """ Returns the named reference if it exists or None otherwise """
        for ref in self.refs:
            if ref.refers_to(name):
                return ref
        return None

