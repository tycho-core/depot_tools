#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Friday, 28 November 2014 01:44:02 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

#pylint: disable=R0921
class PackageBase(object):
    """ package"""
    __metaclass__ = ABCMeta

    class Status(object):
        """ Represents the status of an installed package """

        #pylint: disable=R0913
        def __init__(self, installed, valid, modified, version, 
                     modifications=None, raw_modifications=None):
            """ Constructor """
            self.__installed = installed
            self.__valid = valid
            self.__modified = modified
            self.__version = version

            if modifications:
                self.__modifications = modifications
            else:
                self.__modifications = []

            if raw_modifications:
                self.__raw_modifications = raw_modifications
            else:
                self.__raw_modifications = ''

        def is_installed(self):
            """ Returns true if the package has been installed """
            return self.__installed

        def is_valid(self):
            """ Returns true if the package is installed and is in a valid state """
            return self.__valid

        def is_modified(self):
            """ Returns true if there have been local modifications to the package """
            return self.__modified

        def is_clean(self):
            """ Returns not self.is_modified() """
            return not self.is_modified()

        def is_version(self, version):
            """ Returns true if the version is the passed version """
            return self.get_version() == version

        def get_version(self):
            """ Returns the version of the installed package """
            return self.__version

        def get_modifications(self):
            """ Returns:

            SCM.Modification[] : List of modifications that have been made to the package
            """
            return self.__modifications

        def get_raw_modifications(self):
            """ Returns:
            string : Raw modification text returned from the package provider
            """
            return self.__raw_modifications


    def __init__(self, provider, pkg_name, pkg_version):
        """ Constructor """
        self.provider = provider
        self.name = pkg_name
        self.version = pkg_version
        self.local_path = ''

    def __repr__(self):
        """ Get pretty name for the package for displaying to user """
        return '%s-%s' % (self.name, self.version)

    def display_name(self):
        """ Get pretty name for the package for displaying to user """
        return str(self)

    def is_installed(self, dst_dir):
        """ 
        Returns:
            True if the package has been installed locally """
        return self.local_filesystem_status(dst_dir).is_installed()

    def is_modified(self, dst_dir):
        """
        Returns:
            True if the package has been locally modified
        """
        return self.local_filesystem_status(dst_dir).valid()

    def is_valid(self, dst_dir):
        """
        Returns:
            True if the package appears correctly installed
        """
        return self.local_filesystem_status(dst_dir).is_modified()

    def get_dependencies(self, refresh_dependencies=True):
        """ Returns the packages this package depends on """
        return self.provider.get_package_info(self, refresh_dependencies).get_dependencies()

    @abstractmethod
    def get_package_info(self, refresh_dependencies):
        """ Returns the info for this package """
        pass

    @abstractmethod
    def checkout(self, dst_dir):
        """
        Checkout the package to the local filesystem
        """         
        pass

    @abstractmethod
    def update(self, dst_dir):
        """
        Update the package to the latest version
        """
        pass

    @abstractmethod
    def local_filesystem_status(self, local_dir):
        """
        Returns:
            PackageBase.Status : Status of package in local filesystem
        """
        pass

    @abstractmethod
    def change_version(self, local_dir, force):
        """ Change the local version to the current package version """
        pass

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
