#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 09:05:31 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.scm.git.unit_tests.config import Config
from details.scm.git.thehub import TheHub
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class TestGitHub(TestCase):
    __test_repos = Config.test_repos
    __auth_token = Config.github_auth_token  
    __org_name = Config.github_organization

    def test_construct(self):
        hub = TheHub(TestGitHub.__auth_token, TestGitHub.__org_name)
        self.assertIsNotNone(hub)

    def test_get_hub_project_names(self):
        hub = TheHub(TestGitHub.__auth_token, TestGitHub.__org_name)
        names = hub.get_hub_project_names()

        self.assertEqual(len(names), len(TestGitHub.__test_repos))
        self.assertEqual(len([repo for repo in names if repo not in TestGitHub.__test_repos]), 0)

#-----------------------------------------------------------------------------
# Main
#--------------------------------------------------------------c---------------
if __name__ == "__main__":
    unittest.main()
