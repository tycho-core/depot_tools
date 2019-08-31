import details.utils.misc
from github import Github
from details.utils.misc import add_command_line_action


class TheHub(object):
    """ Interface to query the hub. Uses Github currently. """
    def __init__(self, auth_token, org_name):
        """ Constructor.    
        Args:
            workspace.Workspace : Workspace to use
        """

        self.__auth_token = auth_token
        self.__org_name = org_name
        self.__git_hub = Github(login_or_token=self.__auth_token)
    
    
    def get_hub_project_names(self):
        """
        Get a list of all the repo names within this hub.

        Returns:
            list(string)
        """
        repos = self.get_hub_projects()
        return [ repo.name for repo in repos ]

    def get_hub_projects(self):
        """
        Get a list of all projects in the hub
        
        Returns:
            list(Github.Repository)
        """
        org = self.__git_hub.get_organization(self.__org_name)
        return org.get_repos()
        
    def show_hub_projects(self, existing_deps=None):
        """
        Print list of all projects in the hub to stdout. Each project is preceeded by
        an asterisk if it is already a dependency
        
        Args:
            existing_deps(list(tydepends.Dependency)) : List of existing dependencies or None
        """        
        repos = self.get_hub_projects()
        for repo in repos:            
            if existing_deps and existing_deps.project_exists(repo.name):
                print('* ' + repo.name)
            else:
                print(repo.name)

    def pick_hub_project(self, existing_deps=None):
        """
        Interactively choose a hub project. Only shows projects that are not already workspace
        level dependencies.
        
        Args:
            existing_deps(list(tydepends.Dependency)) : List of existing dependencies or None
            
        Returns:
            Github.Repository
        """
        # prune out existing repos
        all_repos = self.get_hub_projects()        
        repos = []
        if existing_deps == None:
            repos = all_repos
        else:
            for repo in all_repos:
                if not existing_deps.contains_project(repo.name):
                    repos.append(repo)
                    
        if len(repos) == 0:
            print('All projects are existing dependencies')
            return None
                            
        num_repos = 0
        for repo in repos:            
            print('%s : %s' % (num_repos, repo.name))
            num_repos = num_repos + 1
                    
        while True:
            input_ok = True
            try:
                index = int(raw_input('Enter project index : '))
            except:
                input_ok = False
            
            if index < 0 or index >= num_repos:
                input_ok = False
                
            if not input_ok:
                print('Invalid selection')
            else:
                break
            
        return repos[index]
    
    @staticmethod
    def pick_project_branch(project):
        """
        Interactively select a branch for a hub project.
        
        Args:
            project(Github.Repository) : Repository to show branches for.
            
        Returns:
            Github.Branch
        """
        branches = project.get_branches()
        
        num_branches = 0
        for branch in branches:            
            print('%s : %s' % (num_branches, branch.name))
            num_branches = num_branches + 1
                    
        while True:
            input_ok = True
            try:
                index = int(raw_input('Enter branch index : '))
            except:
                input_ok = False
            
            if index < 0 or index >= num_branches:
                input_ok = False
                
            if not input_ok:
                print('Invalid selection')
            else:
                break
        
        return branches[index] 
        
    def select_import(self, existing_deps=None):
        """
        Interactively select a hub project and branch.
        
        Args:
            existing_deps(list(tydepends.Dependency)) : List of existing dependencies or None
            
        Returns:
            list : [ Github.Repository, Github.Branch ] 
        """        
        project = self.pick_hub_project(existing_deps=existing_deps)
        if project == None:
            return None
        print('Selected %s' % (project.name))
        print('')
        branch = TheHub.pick_project_branch(project)
        return [project, branch]
    
    @staticmethod
    def add_command_line_options(parser):
        """
        Add all command line arguments to the main parser. 
        """    
        parser.set_defaults(mode='hub')
        subparsers = parser.add_subparsers()
        
        # list action
        cmd_help = 'Display list of all hub projects'
        sb_help = 'Include sandbox libraries in the output'
        parser = add_command_line_action(subparsers, 'list', action_help=cmd_help)
        parser.add_argument('--sandbox', '-r', action='store_true', help=sb_help)
