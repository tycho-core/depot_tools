#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Friday, 28 November 2014 02:06:12 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from threading import Thread
from details.package.provider_base import ProviderConfig
import details.package.source.git.provider as GitProvider
import details.package.source.http.provider as HttpProvider
from details.package.provider_factory import ProviderFactory
from details.package.source.git.github_query_interface import GitHubQueryInterface
from details.package.source.git.gitlab_query_interface import GitLabQueryInterface
from details.package.provider_query_aggregator import ProviderQueryAggregator
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
        self.__context = context
        # setup providers
        self.__provider_factory = ProviderFactory(context)

        # add provider types
        self.__provider_factory.add_provider_class('git', GitProvider.Provider)
        self.__provider_factory.add_provider_class('http', HttpProvider.Provider)
 
        # add provider query interfaces
        self.__provider_factory.add_provider_query_class('github', GitHubQueryInterface)
        self.__provider_factory.add_provider_query_class('gitlab', GitLabQueryInterface)

        # setup aggregated provider query interface for performing operations
        # on all registered providers
        self.__provider_query_interface = ProviderQueryAggregator()

        # load all providers
        for provider_config in providers:
            config = ProviderConfig(self.__context, provider_config)

            if config.enabled:
                provider = self.__provider_factory.load_provider(config.name,
                                                        config.provider_name,
                                                        config.provider_params,
                                                        config.query_interface_name,
                                                        config.query_interface_params)
                self.__provider_factory.register_provider(config.name, config.provider_name, provider)
                if provider.get_query_interface():
                    self.__provider_query_interface.add_query_interface(provider.get_query_interface())
                vlog('PackageManager : Imported Provider : %s : %s' %
                    (config.name, config.provider_name))

        # package cache
        self.__cache = {}

    def get_package(self, provider_name, pkg_name, pkg_version, check_valid=True, refresh=True):
        """ Get a package from the specified provider """

        # check if we have already cached this
        key = "%s-%s-%s" % (provider_name, pkg_name, pkg_version)
        if key in self.__cache:
            return self.__cache[key]
        provider = self.__provider_factory.get_provider(provider_name)
        pkg = provider.find_package(pkg_name, pkg_version, check_valid, refresh)
        self.__cache[key] = pkg
        return pkg


    def get_package_dependency_tree(self, package):
        """
        Get the full dependency heirarchy for a package.

        Returns:
            Dependency() : Root dependency for this package
        """
        pass            

    def get_aggregated_query_interface(self):
        """ Get a query interfaces that combines all the individual provider query interfaces. """
        return self.__provider_query_interface

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
