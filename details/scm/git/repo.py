#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Wednesday, 03 December 2014 05:52:40 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
import getpass
import re
from details.utils.misc import execute
from details.scm.git.config import Config
from details.utils.url import Url
from details.scm.git.refs import Refs
from details.scm.git.modification import Modification
from details.scm.git.tools import has_credential_helper


#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Repo(object):
    """ This represents a connection between a remote git repository and a 
    local working copy """

    # credentials cache
    credentials_cache = {}

    def __init__(self, remote_url, root_dir=None, anonymous=False):
        """ Constructor """
        assert remote_url

        self.root_dir = None
        self.remote_url = remote_url
        self.credentials = {}
        self.anonymous = anonymous

        if root_dir:
            self.__set_local(root_dir)
 
    def __set_local(self, local_dir):
        """ Set local working directory """
        self.root_dir = local_dir

           # check to see if this is a valid git repo
        if self.is_valid_working_copy():
            # load the git config file
            try:
                config = Config()
                config.load_from_file(os.path.join(self.root_dir, '.git', 'config'))

                # get url for remote origin
                url = config.get_setting('remote', 'origin', 'url')
                if url:
                    self.remote_url = Url(url)
            except():
                pass


    def __set_remote(self, remote_url, anonymous=True, username=None, password=None):
        """ Set the remote host to use and optionally user credentials """
        self.anonymous = anonymous
        self.remote_url = remote_url
        self.remote_url.username = username
        self.remote_url.password = password

        if not anonymous and username and password:
            Repo.credentials_cache[self.remote_url.host] = [username, password]

    def _set_remote_url_and_credentials(self, remote_url):
        """ Ensure we have credentials if required for the remote host """
        self.remote_url = remote_url
        if not has_credential_helper() and not self.anonymous and self.remote_url.needs_credentials():
            if not self.remote_url.username or not self.remote_url.password:
                username, password = Repo.get_credentials(self.remote_url)
                self.remote_url.username = username
                self.remote_url.password = password

    @staticmethod
    def get_credentials(url):
        """ Get the user credentials for this host, will return cached details or query the user
        if they have not been previousy cached """
        if url.host in Repo.credentials_cache:
            return Repo.credentials_cache[url.host]

        # not there so prompt user for details
        username = raw_input('Enter username for %s : ' % url.host)
        password = getpass.getpass('Enter password for %s : ' % url.host.encode('ascii'))

        credentials = [username, password]
        Repo.credentials_cache[url.host] = credentials

        return credentials

    def is_valid_working_copy(self):        
        """ Check that the root points to a valid git repository """
        if not os.path.exists(self.root_dir):
            return False

        if not os.path.isdir(self.root_dir):
            return False

        git_dir = os.path.join(self.root_dir, '.git')

        if not os.path.exists(git_dir):
            return False

        if not os.path.isdir(git_dir):
            return False

        cur_dir = os.getcwd()
        os.chdir(self.root_dir)
        exit_code, _, _ = self.execute_git(['rev-parse', '--git-dir'])
        os.chdir(cur_dir)
        if exit_code == 0:
            return True
        return False

    def repo_name(self):       
        """ Returns the name of this repository """ 
        if self.remote_url:
            path = self.remote_url.path
            if path:
                match = re.match(r'(?:.*/)?(.*)\.git', path)
                if match:
                    return match.group(1)

        return None


    def is_valid_remote(self):
        """ Check that the URL points to a valid remote repository """
        self._set_remote_url_and_credentials(self.remote_url)
        exit_code, _, _ = self.execute_git(['ls-remote', str(self.remote_url)])
        if exit_code == 0:
            return True
        return False
    
    def is_valid_remote_branch(self, branch_name):
        """ Check that the URL points to a valid remote repository and that the branch exists """
        self._set_remote_url_and_credentials(self.remote_url)
        exit_code, refs_str, _ = self.execute_git(['ls-remote', str(self.remote_url)], 
                                                  capture=True)
        if exit_code != 0:
            return False
        refs = Refs.create_from_string(refs_str)
        return refs.has_branch(branch_name)

    def clone(self, capture=True):
        """ Clone a remote repository """
        return self.clone_branch('master', capture=capture)

    def clone_branch(self, branch_name, capture=True):
        """ Clone a specific branch from a remote repository """
        #todo : if repo already exists should we delete and resync
        #       need to check if there have been modificiations
        #if self.is_valid_working_copy():
        #    return
        self._set_remote_url_and_credentials(self.remote_url)
        exit_code, _, _ = self.execute_git(['clone', '-b', branch_name, str(self.remote_url), 
                                            self.root_dir], capture=capture)
        return exit_code == 0

    def pull(self, capture=True):
        """ Pull latest from the remote """
        exitcode, _, _ = self.execute_git(['pull'], capture=capture)
        return exitcode == 0
        
    def add_file(self, file_path, capture=True):
        """ Add a file to the index """
        exitcode, _, _ = self.execute_git(['add', file_path], capture=capture)
        return exitcode == 0
        
    def status(self, capture=True):
        """ Returns status of current working copy """
        return self.execute_git(['status'], capture=capture)
        
    def branch_name(self):
        """ Returns the name of the current branch of the working copy """
        res = self.execute_git(['rev-parse', '--abbrev-ref', 'HEAD'])
        name = res[1].strip()
        return name
    
    def switch_branch(self, branch_name, capture=True):
        """ Switch the local working copy to another existing branch """
        exitcode, _, _ = self.execute_git(['checkout', branch_name], capture=True)
        return exitcode == 0        
    
    def is_clean(self):
        """ Returns true if there are no modification to the local working copy """
        return len(self.get_modifications()) == 0


    def get_modifications(self):
        """ Returns:
            scm.Modification[]  : List of modification made to the working copy """
        exitcode, output, _ = self.execute_git(['status', '--porcelain', '-z'], capture=True)

        if exitcode != 0:
            return None

        # parse output
        return Modification.create_list_from_git_status(output)

    def discard_modifications(self):
        """ Discard all modification to the local working copy. This is irreversable. """
        exitcode, _, _ = self.execute_git(['reset', '--hard', 'HEAD'], capture=True)
        return exitcode == 0

    def stash_modifications(self):
        """ Stash any local modifications to the working copy """
        exitcode, _, _ = self.execute_git(['stash'], capture=True)
        return exitcode == 0

    def unstash_modifications(self):
        """ Stash any local modifications to the working copy """
        exitcode, _, _ = self.execute_git(['stash', 'pop'], capture=True)
        return exitcode == 0

    def execute_git(self, args, capture=True):
        """ Execute a git command """
        return execute('git', self.root_dir, args, capture)
