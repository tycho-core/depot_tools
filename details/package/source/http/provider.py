#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 27 November 2014 06:38:23 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from os import path, makedirs
from details.package.provider_base import ProviderBase, MissingParam, PackageNotFound, ProviderException
from details.utils.url import Url
from details.utils.misc import vlog, ensure_valid_pathname, ensure_trailing_slash, log
import details.utils.file as futils
from details.package.package_info import PackageInfo
from details.package.source.http.package import Package as HttpPackage
import sys
import os

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Provider(ProviderBase):
    """ HttpProvider """
    
    def __init__(self, name, context, params):
        """ Constructor """
        super(Provider, self).__init__(name, context, 'http', versioned=False)

        # host must be specified
        if not 'host' in params:
            raise MissingParam(self, 'host')

        self.host = ensure_trailing_slash(params['host'], sep='/')

        if sys.platform in ['win32', 'cygwin']:
            self.host += 'win32/'
        else:
            self.host += sys.platform + '/'

        self.host_url = Url(self.host)

        # create a temporary directory unique to this host
        self.temp_dir = path.join(context.temp_dir, ensure_valid_pathname(self.host))
            
        if not path.exists(self.temp_dir):
            makedirs(self.temp_dir)

        # create temporary store to cache packages for dependency checking
        self.temp_pkg_dir = path.join(self.temp_dir, 'pkgs')

        if not path.exists(self.temp_pkg_dir):
            makedirs(self.temp_pkg_dir)

        # map of package files to local cache path
        self.__cached_files = {}

    def make_pkg_url(self, pkg_name, pkg_version):
        """ Construct the URL that points to the package """
        return '%s%s/%s' % (str(self.host_url), pkg_name, pkg_version)
    

    def find_package(self, pkg_name, pkg_version):
        vlog('Looking for package %s-%s' % (pkg_name, pkg_version))

        pkg = HttpPackage(self, pkg_name, pkg_version)
        if not self.get_package_info(pkg):
            vlog('Could not find %s-%s' % (pkg_name, pkg_version))
            raise PackageNotFound(self, pkg_name, pkg_version, "Package or version does not exist")

        vlog('Found package %s-%s' % (pkg_name, pkg_version))
        return pkg

    def get_package_info(self, package):
        """
        Get the PackageInfo describing this package

        Returns:
            PackageInfo() : Information about this package
        """
        cached_path = self.cache_package_file(package, self.context.package_info_filename)
        
        if not cached_path:
            return None

        return PackageInfo.create_from_json_file(cached_path)

    def cache_package_file(self, package, rel_path):
        """ Cache a file from the provider locally """
        pkg_url = self.make_pkg_url(package.name, package.version)

        pkg_src_url = '%s/%s' % (pkg_url, rel_path)
        pkg_dst_file = path.join(self.__get_package_cache_dir(package), rel_path)

        if pkg_src_url in self.__cached_files:
            return self.__cached_files[pkg_src_url]

        try:
            vlog('Download %s -> %s' % (pkg_src_url, pkg_dst_file))

            if os.path.exists(pkg_dst_file):
                os.remove(pkg_dst_file)

            futils.download_file(pkg_src_url, pkg_dst_file)
                #raise ProviderException()

            # add to cached
            self.__cached_files[pkg_src_url] = pkg_dst_file
            return pkg_dst_file
        except Exception as ex:
            vlog('Exception : %s' % (str(ex)))
            raise ProviderException(self, "Failed to cache package '%s'" % str(package))
        return None

    def __temp_path(self, rel_path):
        """ returns the path to our temporary file storage """
        return path.join(self.temp_dir, rel_path)

    def __temp_pkg_path(self, rel_path):
        """ returns the path to our temporary repository storage """
        return path.join(self.temp_pkg_dir, rel_path)

    def __get_package_cache_dir(self, pkg):
        """ Returns the directory to use for caching the packages repo """
        cache_dir = self.__temp_pkg_path('%s_%s' % (pkg.name, pkg.version))

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        return cache_dir

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
