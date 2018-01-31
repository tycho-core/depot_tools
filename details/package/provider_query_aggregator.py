#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Wednesday, 11 March 2015 03:17:00 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.package.provider_query_interface import ProviderQueryInterface

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class ProviderQueryAggregator(ProviderQueryInterface):
    """ Aggregates multiple provider query interfaces into a single interface """
    
    def __init__(self):
        """ Constructor """
        self.__interfaces = []

    def add_query_interface(self, interface):
        """ Add a query interface """
        self.__interfaces.append(interface)

    def get_display_name(self):
        """
        Returns:
            string : Pretty name of the query interface to display to user
        """
        return "Aggregated" 

    def get_projects(self):
        """ Returns:
                list(Project) : List of all projects available from all providers 
        """
        projects = []
        for provider in self.__interfaces:
            projects += provider.get_projects()
        return projects

    def get_project_versions(self, project):
        """
        Get a list of versions available for this project.

        Args:
            ProjectBase : Project to get versions for.

        Returns:
            list(VersionBase) : List of available versions for the given project
        """     
        return project.get_versions()


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
