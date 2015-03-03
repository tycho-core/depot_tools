#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Monday, 08 December 2014 10:47:29 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
from details.package.provider_base import MissingParam, PackageNotFound
from details.package.source.git.provider import Provider
from details.scm.git.unit_tests.config import Config as GitConfig
from details.depends import Dependency
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Unit tests
#-----------------------------------------------------------------------------

class TestGitProvider(TestCase):
    """ Tests for details.package.GitProvider """
    __test_pkg_name = GitConfig.test_repo_name
    __test_pkg_versions = ['master', GitConfig.test_branch_name]


    def __make_provider(self):
        # valid params
        test_params = {
            'host' : GitConfig.test_host,
            'anonymous' : False,
            'username' : GitConfig.username,
            'password' : GitConfig.password
        }
        provider = Provider('hub', self.context, test_params)     
        self.assertIsNotNone(provider)
        return provider

    def test_construct(self):
        provider = self.__make_provider()
        self.assertEquals(provider.name, 'git')
        self.assertTrue(provider.is_versioned())

        # missing params
        self.assertRaises(MissingParam, Provider, 'hub', self.context, {})

    def test_find_package(self):
        # find package tests
        provider = self.__make_provider()
        pkg = provider.find_package(TestGitProvider.__test_pkg_name, 'master')
        self.assertIsNotNone(pkg)

        # test invalid package
        self.assertRaises(PackageNotFound, 
                          Provider.find_package,
                          provider,
                          'hubInvalid',
                          'master')

        # test invalid version
        self.assertRaises(PackageNotFound, 
                          Provider.find_package,
                          provider,
                          TestGitProvider.__test_pkg_name,
                          'Tiger')

    def test_get_package_dependencies(self):
        provider = self.__make_provider()
        pkg = provider.find_package(TestGitProvider.__test_pkg_name, 'master')
        self.assertIsNotNone(pkg)
        deps = provider.get_package_dependencies(pkg)
        self.assertIsNotNone(deps)
        self.assertEqual(deps.source, Dependency.SourceRoot)
        self.assertEqual(len(deps.children), 1)
        self.assertTrue(deps.contains(Dependency('hub', 'hubTestProject2', 'master')))
        self.assertFalse(deps.contains(Dependency('hub', 'hubTestProject2', 'branch2')))





#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
