#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 27 November 2014 06:38:09 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from os import path, makedirs
from details.package.provider_base import ProviderBase, MissingParam, PackageNotFound, PackageInfoException
from details.package.package_binding import PackageBinding
from details.package.package_info import PackageInfo
from details.package.source.git.package import Package as GitPackage
from details.scm.git.repo import Repo
from details.scm.git.tools import get_archive_file
from details.utils.url import Url
from details.utils.misc import ensure_valid_pathname, log, vlog
from copy import deepcopy
import details.utils.misc as utils
import details.utils.file as futils
import os

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Provider(ProviderBase):
    """ Git package provider. Provides packages that are hosted on a git server """

    def __init__(self, name, context, params, query_interface):
        """ Constructor """
        super(Provider, self).__init__(name, context, 'git', True, query_interface)

        # host must be specified
        if not 'host' in params:
            raise MissingParam(self, 'host')

        self.host = params['host']
        self.username = None
        self.password = None
        self.anonymous = False
        self.__packages_updated = set()
        self.__package_info_cache = {}

        # username and password are optional
        if 'username' in params and 'password' in params:
            self.username = params['username']
            self.password = params['password']

        if 'anonymous' in params:
            self.anonymous = params['anonymous']

        # create a temporary directory unique to this host
        self.temp_dir = path.join(context.library_cache_path, ensure_valid_pathname(self.host))

        if not path.exists(self.temp_dir):
            makedirs(self.temp_dir)

    def make_pkg_url(self, pkg_name):
        """ Construct the URL that points to the package """
        return '%s/%s.git' % (str(self.host), pkg_name)

    def find_package(self, pkg_name, pkg_version, check_valid, refresh):
        vlog('Looking for package %s-%s' % (pkg_name, pkg_version))
        check_remote = check_valid

        # check that this package exists on the server
        repo = self.__make_remote_repo(pkg_name, '')

        #TODO: This takes the majority of the execution time performing a status, we need
        #      to optimise or cache results somewhere.
        if check_remote and not repo.is_valid_remote_branch(pkg_version):
            vlog('Could not find %s-%s' % (pkg_name, pkg_version))
            raise PackageNotFound(self, pkg_name, pkg_version, "Version does not exist")
        vlog('Found package %s-%s' % (pkg_name, pkg_version))
        return GitPackage(self, pkg_name, pkg_version)

    def get_package_info(self, pkg, refresh=True):
        # get only the typackage.info file from the remote repository
        vlog('Getting package info for %s-%s (refresh=%s)' % (pkg.name, pkg.version, str(refresh)))
        key = '%s-%s-%s' % (self.host, pkg.name, pkg.version)

        json = self.context.cache.load_from_cache(key)
        if not json:
            url = self.make_pkg_url(pkg.name)
            json = get_archive_file(url, pkg.version, 'typackage.info')
            self.context.cache.save_to_cache(json, key, 8 * 60 * 60, 0.25)
        return PackageInfo.create_from_json_string(json)

    def __temp_path(self, rel_path):
        """ returns the path to our temporary file storage """
        return path.join(self.temp_dir, rel_path)

    def __make_remote_repo(self, pkg_name, local_dir):
        """ Returns a Repo object to the remote repository """
        remote_url = self.make_pkg_url(pkg_name)
        anonymous = self.anonymous
        if self.username and self.password:
            remote_url.username = self.username
            remote_url.password = self.password
            anonymous = False
        return Repo(self.context, remote_url, local_dir, anonymous=anonymous)

        

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
