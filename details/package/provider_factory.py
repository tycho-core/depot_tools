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
            super(ProviderFactory.ProviderAlreadyExists, self).__init__()
            self.name = name

        def __str__(self):
            return "Provider '%s' already exists" % (self.name)

    class ProviderDoesNotExist(LookupError): 
        """ Raised if a provider of that name does not exist """

        def __init__(self, name):
            super(ProviderFactory.ProviderDoesNotExist, self).__init__()
            self.name = name

        def __str__(self):
            return "Provider '%s' does not exist" % (self.name)        

    class ProviderClassAlreadyExists(Exception): 
        """ Raised if a class of that name already exists """

        def __init__(self, name):
            super(ProviderFactory.ProviderClassAlreadyExists, self).__init__()
            self.name = name

        def __str__(self):
            return "Provider class '%s' already exists" % (self.name)          

    class ProviderClassDoesNotExist(LookupError): 
        """ Raised if a class of that name does not exist """

        def __init__(self, name):
            super(ProviderFactory.ProviderClassDoesNotExist, self).__init__()
            self.name = name

        def __str__(self):
            return "Provider class '%s' does not exist" % (self.name)          

    def __init__(self, context):
        """ Constructor """
        self.context = context
        self.providers = {}
        self.provider_classes = {}

    def add_provider(self, name, provider_class, provider_params):
        """ Add a provider source """
        if name in self.providers:
            raise ProviderFactory.ProviderAlreadyExists(name)
        if not provider_class in self.provider_classes:
            raise ProviderFactory.ProviderClassDoesNotExist(name)

        provider = self.provider_classes[provider_class](name, self.context, provider_params)
        self.providers[name] = provider

    def add_provider_class(self, name, provider_class):
        """ Add a provider class  """
        if name in self.provider_classes:
            raise ProviderFactory.ProviderClassAlreadyExists(provider_class)
        self.provider_classes[name] = provider_class            

    def get_provider(self, provider_name):
        """ Lookup up a provider by name. 

        Returns:
            Provider() : Provider with the passed name.
            
        Throws:
            ProviderDoesNotExist() : If provider does not exist
        """
        if not provider_name in self.providers:
            raise ProviderFactory.ProviderDoesNotExist(provider_name)
        return self.providers[provider_name]

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
