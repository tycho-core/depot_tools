#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 27 November 2014 06:37:43 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class ProviderConfig(object):
    """ Configuration for a package provider """

    def __init__(self, context, params_dict):
        """ Constructor """
        self.context = context
        self.name = ProviderConfig.__value_or_none(params_dict, 'name')
        self.provider_name = ProviderConfig.__value_or_none(params_dict, 'provider')
        self.provider_params = ProviderConfig.__value_or_none(params_dict, 'provider_params')

    @staticmethod
    def __value_or_none(in_dict, name):
        """ Return value if the key exists or None otherwise """
        if name in in_dict:
            return in_dict[name]
        return None

class ProviderException(Exception): 
    """ Base of all provider exceptions """

    def __init__(self, provider, msg=None):
        """ Constructor """
        super(ProviderException, self).__init__()
        self.provider = provider        
        self.msg = msg

class PackageNotFound(ProviderException): 
    """ A package could not be found """

    def __init__(self, provider, package_name, package_version, reason):
        """ Constructor """
        super(PackageNotFound, self).__init__(provider)
        self.package_name = package_name
        self.package_version = package_version
        self.reason = reason

    def __str__(self):
        return "Provider '%s' failed to find package '%s:%s' : %s" % (self.provider.source_name, 
                                                                      self.package_name,
                                                                      self.package_version,
                                                                      self.reason)

class PackageInfoException(ProviderException):
    """Package info file is not presetn for a package """

    def __init__(self, provider, package_name, package_version, reason):
        """ Constructor """
        super(PackageInfoException, self).__init__(provider)
        self.package_name = package_name
        self.package_version = package_version
        self.reason = reason

    def __str__(self):
        return "No PackageInfo for package '%s:%s'" % (self.package_name,
                                                       self.package_version,
                                                       self.reason)

class MissingParam(ProviderException): 
    """ Required parameter is missing """

    def __init__(self, provider, param_name):
        """ Constructor """
        super(MissingParam, self).__init__(provider)
        self.param_name = param_name

    def __str__(self):
        return "Provider '%s' missing parameter '%s'" % (self.provider.name, self.param_name)

class InvalidParam(ProviderException): 
    """ Provided parameter is invalid """
    
    def __init__(self, provider, param_name, param_value):
        """ Constructor """
        super(InvalidParam, self).__init__(provider)    
        self.param_name = param_name
        self.param_value = param_value

    def __str__(self):
        return "Provider '%s' has invalid value '%s' for parameter '%s'" % (self.provider.source_name, 
                                                                            self.param_value,
                                                                            self.param_name)

#pylint: disable=R0921
class ProviderBase(object):
    """ Package provider """
    __metaclass__ = ABCMeta


    def __init__(self, source_name, context, name, versioned):
        """ Constructor """
        self.context = context
        self.versioned = versioned
        self.name = name
        self.source_name = source_name

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


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
