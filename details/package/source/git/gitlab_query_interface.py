#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Sunday, 22 March 2015 08:01:42 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.package.provider_query_interface import ProviderQueryInterface, ProjectBase, VersionBase
from details.utils.misc import dict_value_or_none, dict_value_or_default
from os import makedirs
import gitlab
import os.path as path
import json

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class GitLabQueryInterface(ProviderQueryInterface):
    """ GitlabQueryInterface """
    AllProjects = None
    QueryCacheTime = 60 * 60 * 24  # 1 day

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

        def __init__(self, project, branch_name):
            """ Constructor """
            super(GitLabQueryInterface.Version, self).__init__(project, branch_name)


    def __init__(self, context, params):
        """ Constructor """
        super(GitLabQueryInterface, self).__init__()
        self.__context = context
        self.__auth_token = dict_value_or_none(params, 'auth_token')
        self.__base_url  = dict_value_or_none(params, 'base_url')
        self.__group = dict_value_or_none(params, 'group')
        self.__cache_expiry = dict_value_or_default(params, 'cache_expiry', GitLabQueryInterface.QueryCacheTime)
        self.__cache_jitter = dict_value_or_default(params, 'cache_jitter', 0.25)

        #TODO : Disabling SSL is not the best idea. Figure out why it is failing to verify (maybe selfsigned)
        self.__gitlab = gitlab.Gitlab(host=self.__base_url, token=self.__auth_token, verify_ssl=True)

        # only call the API once to get all projects and cache in a class static
        if not GitLabQueryInterface.AllProjects:
            projects = context.cache.load_from_cache('gitlab_provider_projects')
            if projects:
                GitLabQueryInterface.AllProjects = projects
            else:
                GitLabQueryInterface.AllProjects = [ project for project in self.__gitlab.getall(self.__gitlab.getprojects) ]
                context.cache.save_to_cache(GitLabQueryInterface.AllProjects, 'gitlab_provider_projects', GitLabQueryInterface.QueryCacheTime)

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
        cache_name = 'gitlab_provider_versions_{0}_{1}'.format(self.__group, project.get_repo()['name'])
        branches = self.__context.cache.load_from_cache(cache_name)
        if not branches:
            branches = [branch['name'] for branch in self.__gitlab.getbranches(project.get_repo()['id'])]
            self.__context.cache.save_to_cache(branches, cache_name, self.__cache_expiry, self.__cache_jitter)

        return [GitLabQueryInterface.Version(project, branch) for branch in branches]



#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
