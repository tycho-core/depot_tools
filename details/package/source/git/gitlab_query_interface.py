# -----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Sunday, 22 March 2015 08:01:42 AM
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from details.package.provider_query_interface import ProviderQueryInterface, ProjectBase, VersionBase
from details.utils.misc import dict_value_or_none, dict_value_or_default
from os import makedirs
import gitlab
import os.path as path
import json

# -----------------------------------------------------------------------------
# Class
# -----------------------------------------------------------------------------


class GitLabQueryInterface(ProviderQueryInterface):
    """ GitlabQueryInterface """
    GitLabServer = None
    QueryCacheTime = 60 * 60 * 24  # 1 day

    class Project(ProjectBase):
        """ Gtihub project """

        def __init__(self, owner, name, branches):
            """ Constructor """
            super(GitLabQueryInterface.Project, self).__init__(owner, name)
            self.name = name
            self.branches = [GitLabQueryInterface.Version(
                self, branch) for branch in branches]

        def get_display_name(self):
            return self.name

    class Version(VersionBase):
        """ Github project version information """

        def __init__(self, project, branch_name):
            """ Constructor """
            super(GitLabQueryInterface.Version, self).__init__(
                project, branch_name)

    def __init__(self, context, params):
        """ Constructor """
        super(GitLabQueryInterface, self).__init__()
        self.__context = context
        self.__auth_token = dict_value_or_none(params, 'auth_token')
        self.__base_url = dict_value_or_none(params, 'base_url')
        self.__group = dict_value_or_none(params, 'group')
        self.__cache_expiry = dict_value_or_default(
            params, 'cache_expiry', GitLabQueryInterface.QueryCacheTime)
        self.__cache_jitter = dict_value_or_default(
            params, 'cache_jitter', 0.25)
        self.__projects = None

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
        if not self.__projects:
            cache_name = 'gitlab_provider_projects_{0}'.format(self.__group)
            cache_objs = self.__context.cache.load_from_cache(cache_name)
            if cache_objs:
                self.__projects = [
                    GitLabQueryInterface.Project(
                        self, project['name'], project['branches'])
                    for project in cache_objs
                ]

            if self.__projects:
                return self.__projects
            else:
                self.__projects = []

                if not GitLabQueryInterface.GitLabServer:
                    GitLabQueryInterface.GitLabServer = gitlab.Gitlab(
                        self.__base_url, private_token=self.__auth_token)
                    GitLabQueryInterface.GitLabServer.auth()

                server = GitLabQueryInterface.GitLabServer
                group = server.groups.list(search=self.__group)
                for group_project in group[0].projects.list():
                    gl_project = server.projects.get(group_project.id)
                    gl_branches = [
                        branch.name for branch in gl_project.branches.list(all=True)]
                    self.__projects.append(GitLabQueryInterface.Project(
                        self, gl_project.name, gl_branches))

                cache_objs = [{
                    'name': project.name,
                    'branches': [version.name for version in project.branches]
                } for project in self.__projects]

                self.__context.cache.save_to_cache(
                    cache_objs, cache_name, GitLabQueryInterface.QueryCacheTime)
        return self.__projects

    def get_project_versions(self, project):
        """
        Get a list of versions available for this project.

        Returns:
            list(Version)
        """
        return project.branches


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass


if __name__ == "__main__":
    main()
