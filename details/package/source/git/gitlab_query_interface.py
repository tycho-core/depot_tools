#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Sunday, 22 March 2015 08:01:42 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.package.provider_query_interface import ProviderQueryInterface, ProjectBase, VersionBase
from details.utils.misc import dict_value_or_none
import gitlab

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class GitLabQueryInterface(ProviderQueryInterface):
    """ GitlabQueryInterface """
    AllProjects = None
    
    class Project(ProjectBase):
        """ Gtihub project """

        def __init__(self, owner, repo):
            """ Constructor """
            super(GitLabQueryInterface.Project, self).__init__(owner, repo['name'])
            self.__repo = repo

        def get_repo(self):
            """ Returns :
                    GitHub.Repository : repository for this project
            """
            return self.__repo

        def namespace(self):
            return self.__repo['namespace']

    class Version(VersionBase):
        """ Github project version information """

        def __init__(self, project, branch):
            """ Constructor """
            super(GitLabQueryInterface.Version, self).__init__(project, branch['name'])
            self.__branch = branch

        def get_branch(self):
            """ Returns : 
                GitHub.Branch : branch for this version 
            """
            return self.__branch

    def __init__(self, params):
        """ Constructor """
        self.__auth_token = dict_value_or_none(params, 'auth_token')
        self.__base_url  = dict_value_or_none(params, 'base_url')
        self.__group = dict_value_or_none(params, 'group')

        #TODO : Disabling SSL is not the best idea. Figure out why it is failing to verify (maybe selfsigned)
        self.__gitlab = gitlab.Gitlab(host=self.__base_url, token=self.__auth_token, verify_ssl=True)

        # only call the API once to get all projects and cache in a class static
        if not GitLabQueryInterface.AllProjects:
            GitLabQueryInterface.AllProjects = [ project for project in self.__gitlab.getall(self.__gitlab.getprojects) ]

    def get_display_name(self):
        """
        Returns:
            string : Pretty name of the query interface to display to user
        """
        return "GitLab[%s]" % self.__group
            
    def get_projects(self):
        """
        Get a list of all the projects available from this provider.

        Returns:
            list(string)
        """
        results = []
        for gl_project in GitLabQueryInterface.AllProjects:
            project = GitLabQueryInterface.Project(self, gl_project)
            namespace = project.namespace()
            if namespace['name'] == self.__group:
                results.append(project)
        return results
        
    def get_project_versions(self, project):
        """
        Get a list of versions available for this project.

        Returns:
            list(Version)
        """
        versions = []
        for branch in self.__gitlab.getbranches(project.get_repo()['id']):
            #print branch
            versions.append(GitLabQueryInterface.Version(project, branch))

        return versions

        

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
