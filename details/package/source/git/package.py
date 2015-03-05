#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Wargaming.net
# Created : Saturday, 31 January 2015 11:06:45 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.package.package_base import PackageBase
from details.scm.git.repo import Repo
from details.utils.url import Url
from details.utils.misc import log, vlog
from details.package.provider_base import PackageNotFound
import os

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Package(PackageBase):
    """ Manages a git repository """
    def __init__(self, provider, pkg_name, pkg_version):
        super(Package, self).__init__(provider, pkg_name, pkg_version)
        self.provider = provider
        self.local_dir = None
        self.repo_url = provider.make_pkg_url(pkg_name)
        self.package_info = None


    def __make_repo(self, local_dir):
        """ Returns a git.Repo object """
        provider = self.provider
        remote_url = self.repo_url
        if provider.username and provider.password:
            remote_url.username = provider.username
            remote_url.password = provider.password

        return Repo(remote_url, root_dir=local_dir)

    def get_package_info(self, refresh=True):
        """ Returns the info for this package """

        # check if we have them already cached
        if self.package_info:
            return self.package_info

        # not cache so grab the repo
        self.package_info = self.provider.get_package_info(self, refresh)
        return self.package_info


    def checkout(self, local_dir):
        """ Clone the repository to the passed local directory """
        vlog('Checking out %s -> %s' % (self.display_name(), local_dir))
        # fail if the repository already exists
        if os.path.exists(local_dir):
            log('  Failed : Directory already exists')
            return False

        repo = self.__make_repo(local_dir)
        os.makedirs(local_dir)
        if not repo.clone_branch(self.version):
            log('  Failed : Could not checkout')
            raise PackageNotFound(self, self.provider, self.name, 
                                  self.version, "Could not be checked out")
        return True


    def update(self, local_dir):
        if not self.is_installed(local_dir):
            return False
        repo = self.__make_repo(local_dir)
        repo.pull(capture=False)
        return True

    def change_version(self, local_dir, force):
        status = self.local_filesystem_status(local_dir)
        if not status.is_installed():
            self.checkout(local_dir)
            return True
        elif status.get_version() != self.version:
            repo = self.__make_repo(local_dir)
            switch = False
            if not status.is_modified():
                switch = True
            else:
                if force:
                    switch = True
                    if not repo.stash_modifications():
                        log("Failed to stash modifications to %s" % local_dir)
                        return False
                    else:
                        log("Stashed modifications to %s" % local_dir)                        
                else:
                    return False
            if switch:
                return repo.switch_branch(self.version)
        return True                    

    def local_filesystem_status(self, local_dir):
        """ Returns the status of the local package """
        version = ''
        valid = False
        installed = False
        modified = False
        raw_modifications = None
        modifications = None

        repo = self.__make_repo(local_dir)

        # check directory exists
        installed = os.path.exists(local_dir)
        if installed:
            valid = repo.is_valid_working_copy()

            if valid:
                version = repo.branch_name()
                modified = not repo.is_clean()
                if modified:
                    raw_modifications = repo.status(capture=True)[1]

                    # get git mods and translate to common mods
                    modifications = repo.get_modifications()


        return PackageBase.Status(installed=installed,
                                  valid=valid,
                                  modified=modified,
                                  version=version,
                                  raw_modifications=raw_modifications,
                                  modifications=modifications)

    # def __is_installed(self, local_dir):
    #     self.repo.set_local(local_dir)

    #     # check we have a valid repo
    #     if not self.repo.is_valid_working_copy():
    #         return False

    #     # check it is the correct repo
    #     if self.repo.repo_name() != self.name:
    #         return False

    #     # check it is the correct branch
    #     if self.repo.branch_name() != self.version:
    #         return False

    #     return True

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
