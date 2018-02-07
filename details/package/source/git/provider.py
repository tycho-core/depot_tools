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
        self.host_url = Url(self.host)
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

        # create temporary store to cache repositories for dependency checking
        self.temp_repo_dir = path.join(self.temp_dir, 'repos')

        if not path.exists(self.temp_repo_dir):
            makedirs(self.temp_repo_dir)

    def make_pkg_url(self, pkg_name):
        """ Construct the URL that points to the package """
        return Url('%s/%s.git' % (str(self.host_url), pkg_name))

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

    #TODO: try using git archive --remote=git@gitlab.com:tychohub-core/depot_tools.git HEAD tyworkspace.info
    #      to avoid cloning the entire package.
    def get_package_info(self, pkg, refresh=True):
        # check to see if we have cached the info for this package. If not
        # then we need to sync the entire repository so we can get at them. Would be ideal
        # to not need to do this....
        vlog('Getting package info for %s-%s (refresh=%s)' % (pkg.name, pkg.version, str(refresh)))
        key = '%s-%s' % (pkg.name, pkg.version)        

        cached_pkg_info = self.__get_cached_package_info(pkg)

        if not cached_pkg_info or (refresh and not key in self.__packages_updated):
            vlog('Caching packing info...')
            cached_pkg = pkg
            cache_dir = self.__get_package_cache_dir(cached_pkg)
            bound_pkg = PackageBinding(cached_pkg, cache_dir)
            if bound_pkg.is_installed():
                if refresh:
                    bound_pkg.update()
                    self.__packages_updated.add(key)
            else:
                bound_pkg.checkout()

            cached_pkg_info = self.__get_cached_package_info(cached_pkg)

        if not cached_pkg_info:
            raise PackageInfoException(self, pkg.name, pkg.version, '')

        return cached_pkg_info        
      
    def __temp_path(self, rel_path):
        """ returns the path to our temporary file storage """
        return path.join(self.temp_dir, rel_path)

    def __temp_repo_path(self, rel_path):
        """ returns the path to our temporary repository storage """
        return path.join(self.temp_repo_dir, rel_path)

    def __get_package_cache_dir(self, pkg):
        """ Returns the directory to use for caching the packages repo """
        return self.__temp_repo_path('%s_%s' % (pkg.name, pkg.version))

    def __make_remote_repo(self, pkg_name, local_dir):
        """ Returns a Repo object to the remote repository """
        remote_url = self.make_pkg_url(pkg_name)
        anonymous = self.anonymous
        if self.username and self.password:
            remote_url.username = self.username
            remote_url.password = self.password
            anonymous = False
        return Repo(self.context, remote_url, local_dir, anonymous=anonymous)

    @staticmethod
    def __clean_package_repo_cache(cache_dir):
        """ Clear out the cached version of this repo if it exists """
        if os.path.exists(cache_dir):
            root = futils.get_directory_tree(cache_dir)
            if root:
                root.delete()
                os.remove(cache_dir)

    def __check_package_repo_cache(self, pkg_name, cache_dir):
        """ Returns true if the passed cache directory appears intact """
        # check path exists and it is a directory
        if not path.exists(cache_dir) or not path.isdir(cache_dir):
            return False

        # check that it is a valid git repository
        cache_repo = self.__make_remote_repo(pkg_name, cache_dir)
        if not cache_repo.is_valid_working_copy():
            return False

        return True

    def __get_cached_package_info(self, pkg):
        """ check the dependency cache for this package """
        cache_dir = self.__get_package_cache_dir(pkg)

        if cache_dir in self.__package_info_cache:
            return self.__package_info_cache[cache_dir]

        if not self.__check_package_repo_cache(pkg.name, cache_dir):
            Provider.__clean_package_repo_cache(cache_dir)
            return None

        # get the dependency file
        dep_file = os.path.join(cache_dir, self.context.package_info_filename)
        if not os.path.exists(dep_file):
            return None

        pkg_info = PackageInfo.create_from_json_file(dep_file)
        self.__package_info_cache[cache_dir] = pkg_info
        
        return pkg_info

    def __cache_dependencies(self, pkg):
        """ Cache the dependencies for the passed package locally """
        cache_dir = self.__get_package_cache_dir(pkg)
        cache_repo = Repo(cache_dir)
        cache_repo.clone_branch(pkg.remote_url, pkg.version)

        

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
