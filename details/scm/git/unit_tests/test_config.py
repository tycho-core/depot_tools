#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 09:04:55 AM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
import textwrap
from details.scm.git.config import Config
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class TestConfig(TestCase):
    def test_construct(self):
        config = Config()
        self.assertTrue(len(config.branches) == 0)
        self.assertTrue(len(config.remotes) == 0)
        self.assertTrue(len(config.branches) == 0)

    def test_load_from_string(self):
        config_contents = """
            [core]
                repositoryformatversion = 0
                filemode = false
                bare = false
                logallrefupdates = true
                symlinks = false
                ignorecase = true
                hideDotFiles = dotGitOnly
            [remote "origin"]
                url = http://my.server.com/git/depot_tools.git
                fetch = +refs/heads/*:refs/remotes/origin/*
            [branch "master"]
                remote = origin
                merge = refs/heads/master
            [branch "branch_name"]
                remote = origin
                merge = refs/heads/branch_name 
        """

        config = Config()
        config.load_from_string(textwrap.dedent(config_contents))
        self.assertEqual(config.get_core_setting('repositoryformatversion'), '0')
        self.assertEqual(config.get_core_setting('filemode'), 'false')
        self.assertEqual(config.get_core_setting('bare'), 'false')
        self.assertEqual(config.get_core_setting('logallrefupdates'), 'true')
        self.assertEqual(config.get_core_setting('ignorecase'), 'true')
        self.assertEqual(config.get_core_setting('hideDotFiles'), 'dotGitOnly')
        self.assertEqual(config.get_remote_setting('origin', 'url'), 'http://my.server.com/git/depot_tools.git')
        self.assertEqual(config.get_remote_setting('origin', 'fetch'),'+refs/heads/*:refs/remotes/origin/*')
        self.assertEqual(config.get_branch_setting('master', 'remote'), 'origin')
        self.assertEqual(config.get_branch_setting('master', 'merge'), 'refs/heads/master')
        self.assertEqual(config.get_branch_setting('branch_name', 'remote'), 'origin')
        self.assertEqual(config.get_branch_setting('branch_name', 'merge'), 'refs/heads/branch_name')

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
