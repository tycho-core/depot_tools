#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 27 November 2014 06:47:28 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class ProviderFactory(object):  
    """ Provider factory """

    class ProviderAlreadyExists(Exception): 
        """ Raised if a provider of that name already exists """

        def __init__(self, name):
            msg = "Provider '%s' already exists" % (name)

            super(ProviderFactory.ProviderAlreadyExists, self).__init__(msg)

    class ProviderDoesNotExist(LookupError): 
        """ Raised if a provider of that name does not exist """

        def __init__(self, name):
            msg = "Provider '%s' does not exist" % (name)        
            super(ProviderFactory.ProviderDoesNotExist, self).__init__(msg)

    class ProviderClassAlreadyExists(Exception): 
        """ Raised if a class of that name already exists """

        def __init__(self, name):
            msg = "Provider class '%s' already exists" % (name)          
            super(ProviderFactory.ProviderClassAlreadyExists, self).__init__(msg)

    class ProviderClassDoesNotExist(LookupError): 
        """ Raised if a class of that name does not exist """

        def __init__(self, name):
            msg = "Provider class '%s' does not exist" % (name)          
            super(ProviderFactory.ProviderClassDoesNotExist, self).__init__(msg)

    def __init__(self, context):
        """ Constructor """
        self.__context = context
        self.__providers = {}
        self.__provider_classes = {}
        self.__provider_query_classes = {}

    def load_provider(self, name, provider_class, provider_params, query_interface_name, query_interface_params):
        """ Load a provider source """
        query_interface = None
        if query_interface_name and query_interface_params:
            if not query_interface_name in self.__provider_query_classes:
                raise ProviderFactory.ProviderClassDoesNotExist(query_interface_name)
            query_interface = self.__provider_query_classes[query_interface_name](query_interface_params)

        return self.__provider_classes[provider_class](name, self.__context, provider_params, query_interface)


    def register_provider(self, name, provider_class, provider):
        """ Register a provider source previously loaded with load_provider """
        if name in self.__providers:
            raise ProviderFactory.ProviderAlreadyExists(name)
        if not provider_class in self.__provider_classes:
            raise ProviderFactory.ProviderClassDoesNotExist(name)
        self.__providers[name] = provider


    def add_provider_class(self, name, provider_class):
        """ Add a provider class  """
        if name in self.__provider_classes:
            raise ProviderFactory.ProviderClassAlreadyExists(provider_class)
        self.__provider_classes[name] = provider_class            

    def add_provider_query_class(self, name, query_class):
        """ Add a provider query class """
        if name in self.__provider_query_classes:
            raise ProviderFactory.ProviderClassAlreadyExists(query_class)
        self.__provider_query_classes[name] = query_class

    def get_provider(self, provider_name):
        """ Lookup up a provider by name. 

        Returns:
            Provider() : Provider with the passed name.
            
        Throws:
            ProviderDoesNotExist() : If provider does not exist
        """
        if not provider_name in self.__providers:
            raise ProviderFactory.ProviderDoesNotExist(provider_name)
        return self.__providers[provider_name]

    def get_provider_query_interface(self):
        """ Returns :
                ProviderQueryInterface : Interface to query all attached providers 
        """
        return self.__provider_query_interface

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
