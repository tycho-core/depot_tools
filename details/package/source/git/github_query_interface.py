#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Wednesday, 11 March 2015 11:19:42 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.package.provider_query_interface import ProviderQueryInterface, ProjectBase, VersionBase
from details.utils.misc import dict_value_or_none
from github import Github

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class GitHubQueryInterface(ProviderQueryInterface):
    """ Interface to query GitHub  """
    
    class Project(ProjectBase):
    	""" Gtihub project """

    	def __init__(self, owner, repo):
    		""" Constructor """
    		super(GitHubQueryInterface.Project, self).__init__(owner, repo.name)
    		self.__repo = repo

    	def get_repo(self):
    		""" Returns :
    				GitHub.Repository : repository for this project
    		"""
    		return self.__repo

    class Version(VersionBase):
    	""" Github project version information """

    	def __init__(self, project, branch):
    		""" Constructor """
    		super(GitHubQueryInterface.Version, self).__init__(project, branch.name)
    		self.__branch = branch

    	def get_branch(self):
    		""" Returns : 
    			GitHub.Branch : branch for this version 
    		"""
    		return self.__branch

    def __init__(self, params):
        """ Constructor """
        self.__auth_token = dict_value_or_none(params, 'auth_token')
        self.__org_name = dict_value_or_none(params, 'org_name')
        self.__base_url = dict_value_or_none(params, 'base_url')
        self.__git_hub = Github(login_or_token=self.__auth_token, base_url=self.__base_url)
            
    def get_projects(self):
        """
        Get a list of all the projects available from this provider.

        Returns:
            list(string)
        """
        repos = self.__get_repos()
        return [ GitHubQueryInterface.Project(self, repo) for repo in repos ]

    def get_project_versions(self, project):
    	"""
    	Get a list of versions available for this project.

    	Returns:
    		list(string)
    	"""
    	return [ GitHubQueryInterface.Version(project, branch) for branch in project.get_repo().get_branches() ]

    def __get_repos(self):
        """
        Get a list of all projects in the hub
        
        Returns:
            list(Github.Repository)
        """
        org = self.__git_hub.get_organization(self.__org_name)
        return org.get_repos()
        
#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
