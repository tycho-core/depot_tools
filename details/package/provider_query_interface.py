#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Wednesday, 11 March 2015 11:15:46 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from details.utils.misc import log_banner

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------


class VersionBase(object):
    """ Base class for project version information """
    __metaclass__ = ABCMeta

    def __init__(self, owner, name):
        """ Constructor """
        self.__owner = owner
        self.__name = name

    def get_display_name(self):
        """ Returns : 
                string : User friendly name for showing to user 
        """
        return self.__name


class ProjectBase(object):
    """ Base class for provider project """
    __metaclass__ = ABCMeta

    def __init__(self, owner, name):
        """ Constructor """
        self.__name = name
        self.__owner = owner

    def get_display_name(self):
        """ Returns : 
                string : User friendly name for showing to user """
        return self.__name

    def get_versions(self):
        """ Returns : 
                list(VersionBase)  : List of available versions for this project
        """
        return self.__owner.get_project_versions(self)

    def get_owner(self):
        return self.__owner

class ProviderQueryInterface(object):
    """ ProviderQueryInterface """
    __metaclass__ = ABCMeta

    
    def __init__(self):
        """ Constructor """
        pass
            
    def set_provider(self, provider):
        self.__provider = provider

    def get_provider(self):
        return self.__provider

    @abstractmethod
    def get_display_name(self):
        """
        Returns:
            string : Pretty name of the query interface to display to user
        """
        pass
        
    @abstractmethod
    def get_projects(self):
        """
        Get a list of all the projects available from this provider.

        Returns:
            list(Project) : List of all available projects from this provider
        """
        pass

    @abstractmethod
    def get_project_versions(self, projects):
        """
        Get a list of versions available for this project.

        Args:
            ProjectBase : Project to get versions for.

        Returns:
            list(VersionBase) : List of available versions for the given project
        """
        pass


class InteractiveQueryInterface(object):
    """ Interactive console interface to querying providers """

    def __init__(self, query_interface):
        """ Constructor """
        self.__query_interface = query_interface

    def print_projects(self, existing_deps=None):
        """
        Print list of all projects in the hub to stdout. Each project is preceeded by
        an asterisk if it is already a dependency

        Args:
            existing_deps(list(depends.Dependency)) : List of existing dependencies or None
        """        
        projects = self.__query_interface.get_projects()
        for project in projects:            
            name = project.get_display_name()
            if existing_deps and existing_deps.project_exists(name):
                print '* %s:%s' % (project.get_owner().get_provider().source_name, name)
            else:
                print '%s:%s' % (project.get_owner().get_provider().source_name, name)


    def pick_project(self, existing_deps=None):
        """
        Interactively choose a hub project. Only shows projects that are not already workspace
        level dependencies.
        
        Args:
            existing_deps(list(wgdepends.Dependency)) : List of existing dependencies or None
            
        Returns:
            Github.Repository
        """
        # prune out existing repos
        all_projects = self.__query_interface.get_projects()        
        projects = []
        if existing_deps == None:
            projects = all_projects
        else:
            for project  in all_projects:
                if not existing_deps.contains_project(project.get_display_name()):
                    projects.append(project)
                    
        if len(projects) == 0:
            print 'All projects are existing dependencies'
            return None
                            
        num_projects = 0
        for project in projects:            
            print '[%s] %s:%s' % (num_projects, project.get_owner().get_provider().source_name, project.get_display_name())
            num_projects += 1
                
        print ''
        print '[Q] Quit'    
        print ''
        while True:
            input_ok = True
            index = -1
            exit = False
            try:
                ch = raw_input('Enter project index : ')                
                if ch == "q" or ch == "Q":              
                    exit = True
                else:
                    index = int(ch)
            except:
                input_ok = False
            
            if exit:
                import sys
                sys.exit()

            if index < 0 or index >= num_projects:
                input_ok = False
                
            if not input_ok:
                print 'Invalid selection'
            else:
                break
            
        return projects[index]


    @staticmethod
    def pick_project_version(project):
        """
        Interactively select a version for a hub project.
        
        Args:
            project(Project) : Project to show versions for.
            
        Returns:
            Github.Branch
        """
        versions = project.get_versions()
        
        num_versions = 0
        for version in versions:            
            print '[%s] %s:%s' % (num_versions, project.get_display_name(), version.get_display_name())
            num_versions += 1
                    
        print ''
        while True:
            input_ok = True
            index = -1
            try:
                index = int(raw_input('Enter version index : '))
            except:
                input_ok = False
            
            if index < 0 or index >= num_versions:
                input_ok = False
                
            if not input_ok:
                print 'Invalid selection'
            else:
                break
        
        return versions[index]         

    def select_import(self, existing_deps=None):
        """
        Interactively select a hub project and branch.
        
        Args:
            existing_deps(list(wgdepends.Dependency)) : List of existing dependencies or None
            
        Returns:
            list : [ Github.Repository, Github.Branch ] 
        """        
        log_banner('Select project')
        project = self.pick_project(existing_deps=existing_deps)
        if project == None:
            return None
        print ''
        log_banner('Select version')
        version = self.pick_project_version(project)
        return [project, version]

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
