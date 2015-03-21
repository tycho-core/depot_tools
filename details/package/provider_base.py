#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 27 November 2014 06:37:43 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from details.utils.misc import dict_value_or_none

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class ProviderConfig(object):
    """ Configuration for a package provider """

    def __init__(self, context, params_dict):
        """ Constructor """
        self.context = context
        self.name = dict_value_or_none(params_dict, 'name')
        self.provider_name = dict_value_or_none(params_dict, 'provider')
        self.provider_params = dict_value_or_none(params_dict, 'provider_params')
        self.query_interface_name = dict_value_or_none(params_dict, 'query_interface')
        self.query_interface_params = dict_value_or_none(params_dict, 'query_interface_params')
        self.enabled = dict_value_or_none(params_dict, 'enabled')
        if self.enabled is None:
            self.enabled = True

class ProviderException(Exception): 
    """ Base of all provider exceptions """

    def __init__(self, provider, msg=None):
        """ Constructor """
        super(ProviderException, self).__init__(msg)
        self.provider = provider        
        self.msg = msg

class PackageNotFound(ProviderException): 
    """ A package could not be found """

    def __init__(self, provider, package_name, package_version, reason):
        """ Constructor """
        msg = "Provider '%s' failed to find package '%s:%s' : %s" % (provider.source_name, 
                                                                     package_name,
                                                                     package_version,
                                                                     reason)

        super(PackageNotFound, self).__init__(provider, msg)
        self.package_name = package_name
        self.package_version = package_version
        self.reason = reason

class PackageInfoException(ProviderException):
    """Package info file is not presetn for a package """

    def __init__(self, provider, package_name, package_version, reason):
        """ Constructor """
        msg = "No PackageInfo for package '%s:%s'" % (package_name,
                                                      package_version)

        if reason and len(reason) > 0:
            msg += ' - ' + reason

        super(PackageInfoException, self).__init__(provider, msg)

class MissingParam(ProviderException): 
    """ Required parameter is missing """

    def __init__(self, provider, param_name):
        """ Constructor """
        msg = "Provider '%s' missing parameter '%s'" % (provider.name, param_name)
        super(MissingParam, self).__init__(provider, msg)
        

class InvalidParam(ProviderException): 
    """ Provided parameter is invalid """
    
    def __init__(self, provider, param_name, param_value):
        """ Constructor """
        msg = "Provider '%s' has invalid value '%s' for parameter '%s'" % (provider.source_name, 
                                                                           param_value,
                                                                           param_name)

        super(InvalidParam, self).__init__(provider, msg)    

#pylint: disable=R0921
class ProviderBase(object):
    """ Package provider """
    __metaclass__ = ABCMeta


    def __init__(self, source_name, context, name, versioned, query_interface):
        """ Constructor """
        self.context = context
        self.versioned = versioned
        self.name = name
        self.source_name = source_name
        self.__query_interface = query_interface
        if self.__query_interface:
            self.__query_interface.set_provider(self)

    @abstractmethod
    def find_package(self, pkg_name, pkg_version, refresh):
        """
        Get the package from this provider.

        Returns:
            package.Package()
        """
        pass

    @abstractmethod
    def get_package_info(self, package, refresh):
        """
        Get the PackageInfo describing this package

        Returns:
            PackageInfo() : Information about this package
        """
        pass

    def get_package_dependencies(self, package, refresh=True):
        """
        Get the packages a package depends on.

        Returns:
            Dependency() : Dependencies for this package    
        """
        pkg_info = self.get_package_info(package, refresh)
        return pkg_info.get_dependencies()        

    def is_versioned(self):
        """
        Returns:
            True if the package is under version control
        """
        return self.versioned

    def get_query_interface(self):
        """ Returns:
                ProviderQueryInterface : Interface to query provider or None if import
                cannot be queried 
        """
        return self.__query_interface

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
