#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Friday, 28 November 2014 02:06:12 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.package.provider_base import ProviderConfig
import details.package.source.git.provider as GitProvider
import details.package.source.http.provider as HttpProvider
import details.package.source.p4.provider as P4Provider
from details.package.provider_factory import ProviderFactory
from details.utils.misc import vlog

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class PackageManager(object):
    """
    Package manager.
    """

    class PackageManagerException(Exception):
        """ Base class of all PackageManager exceptions """
        pass

    class PackageProviderNotFound(PackageManagerException):
        """ Thrown when a package provider cannot be found """
        pass

    def __init__(self, context, providers):
        self.context = context
        # setup providers
        self.provider_factory = ProviderFactory(context)

        # add provider types
        self.provider_factory.add_provider_class('git', GitProvider.Provider)
        self.provider_factory.add_provider_class('http', HttpProvider.Provider)
 
        # add providers
        for provider in providers:
            config = ProviderConfig(self.context, provider)
            self.provider_factory.add_provider(config.name, config.provider_name, 
                                               config.provider_params)
            vlog('PackageManager : Imported Provider : %s : %s' % 
                 (config.name, config.provider_name))
            
    def get_package(self, provider_name, pkg_name, pkg_version):
        """ Get a package from the specified provider """
        provider = self.provider_factory.get_provider(provider_name)
        return provider.find_package(pkg_name, pkg_version)


    def get_package_dependency_tree(self, package):
        """
        Get the full dependency heirarchy for a package.

        Returns:
            Dependency() : Root dependency for this package
        """
        pass            

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
