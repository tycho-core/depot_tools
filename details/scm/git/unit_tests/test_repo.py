#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 09:05:04 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
import os
from details.scm.git.repo import Repo
from details.scm.git.unit_tests.config import Config
from details.test_case import TestCase
from details.utils.url import Url
from details.utils.misc import ensure_valid_pathname

#-----------------------------------------------------------------------------
# Unit Tests
#-----------------------------------------------------------------------------

class TestGitRepo(TestCase):
    def __make_test_repo_aux(self, remote_url_str):        
        repo_dir = os.path.join(self.context.temp_dir, ensure_valid_pathname(remote_url_str), 
                                Config.test_repo_name)
        os.makedirs(repo_dir)
        remote_url = Url(remote_url_str)
        remote_url.username = Config.username
        remote_url.password = Config.password

        return Repo(remote_url, repo_dir)

    def __make_test_repo(self):        
        return self.__make_test_repo_aux(Config.test_repo_url)

    def __make_test_invalid_repo(self):        
        return self.__make_test_repo_aux(Config.test_repo_invalid_url)

    def __clone_test_repo(self):
        repo = self.__make_test_repo()
        self.assertTrue(repo.clone(Config.test_repo_url))
        return repo


    def test_construct(self):
        repo = self.__make_test_repo()
        self.assertIsNotNone(repo)

    def test_clone(self):
        repo = self.__clone_test_repo()

        # test Repo.is_valid_working_copy()
        self.assertTrue(repo.is_valid_working_copy())

        # test Repo.is_clean()
        self.assertTrue(repo.is_clean())

        # test Repo.branch_name
        self.assertEquals(repo.branch_name(), 'master')

        # test Repo.repo_name
        self.assertEquals(repo.repo_name(), Config.test_repo_name)


    def test_clone_branch(self):
        repo = self.__make_test_repo()

        # test Repo.clone_branch()
        self.assertTrue(repo.clone_branch('branch1'))

    def test_remotes(self):
        repo = self.__make_test_repo()
        invalid_repo = self.__make_test_invalid_repo()

        # test valid remote
        self.assertTrue(repo.is_valid_remote())

        # test invalid remote
        self.assertFalse(invalid_repo.is_valid_remote())

        # test valid remote branch
        self.assertTrue(repo.is_valid_remote_branch('master'))
        self.assertTrue(repo.is_valid_remote_branch('branch1'))

        # test invalid remote branch
        self.assertFalse(invalid_repo.is_valid_remote_branch('tiger'))
        self.assertFalse(repo.is_valid_remote_branch('tiger'))


    def test_switch_branch(self):
        repo = self.__clone_test_repo()
        self.assertTrue(repo.switch_branch('branch1'))
        self.assertTrue(repo.branch_name(), 'branch1')
        self.assertTrue(repo.is_clean())
        self.assertTrue(repo.switch_branch('master'))
        self.assertTrue(repo.branch_name(), 'master')
        self.assertTrue(repo.is_clean())


    def test_is_clean(self):
        repo = self.__clone_test_repo()
        self.assertTrue(repo.is_clean())

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
