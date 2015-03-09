#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 11:04:58 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
import os.path
import argparse
import json
import six
from details.depends import print_conflicts
from details.utils.misc import fatal_error, log, add_command_line_action, log_banner
from details.utils.file import  get_directory_tree
from details.scm.git.thehub import TheHub
from details.template import Template
from details.templateengine import TemplateEngine
from details.workspace_mapping import WorkspaceMapping
from details.package.package_manager import PackageManager
from details.package.package_set import PackageSet
from details.workspace_info import WorkspaceInfo

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Workspace(object):
    """ Object representing the current workspace."""

    def __init__(self, context, root_dir, refresh_dependencies = True):
        """ Constructor """

        # root directory of the workspace
        self.root_dir = root_dir

        # execution context information
        self.context = context
        self.__package_set = None
        self.__mappings = None
        self.__info = None

        context.console.write_line('Initialising workspace')        

        # configure providers
        context.console.start_task('Configuring providers')
        provider_file = open(os.path.join(context.config_dir, 'hub-providers.json'), 'r')
        providers = json.load(provider_file)
        provider_file.close()
        self.context.package_manager = PackageManager(self.context, providers)
        context.console.end_task()


        # load workspace info file and setup mappings
        self.__info = WorkspaceInfo.create_from_json_file(self.get_workspace_info_path())

        context.console.start_task('Processing dependencies')
        self.__package_set = PackageSet.create_from_dependency(self.context, 
                                                               self.__info.get_dependencies(),
                                                               refresh_dependencies)
        context.console.end_task()

        # setup the mappings
        mappings = WorkspaceMapping(self.root_dir)

        # apply global mappings
        default_mapping_path = os.path.join(self.context.config_dir, 
                                            'default_workspace_mappings.json')

        if os.path.exists(default_mapping_path):
            mappings.load_templates_from_json_file(default_mapping_path)
            self.__mappings = mappings

        # apply workspace mappings
        mappings.load_templates_from_dict(self.__info.get_workspace_mappings())

        # set on context 
        self.context.filesystem_mappings = mappings

        # bind the packages into the workspace
        self.__package_set.bind_packages(mappings, refresh_dependencies)

    @staticmethod
    def create_new_workspace(context, root_dir, quiet=False):        
        """
        Initialize a new workspace. 
        
        1) copy default workspace files from templates/workspace
        2) perform a workspace update to get any default libraries
        """
        if len(os.listdir(root_dir)):
            # check whether to clean out directory
            if quiet:
                fatal_error("Workspace already exists")
            else:
                answer = raw_input("Delete all contents of %s? (y/N)" % root_dir)
                if answer != 'y':
                    fatal_error("Workspace already exists")

                log('Deleting all existing files')
                dir_tree = get_directory_tree(root_dir)
                dir_tree.delete()

        
        # load the workspace template
        template_info_path = os.path.join(context.workspace_layout_path, 
                                          context.template_info)

        template = Template.load_from_file(context, template_info_path)
        engine = TemplateEngine(context)
        engine.expand_template(template, {}, root_dir)

        return True


    def update(self, force=False, preview=False):
        """
        Update the workspace in the passed directory. This will ensure that all 
        dependencies have been retrieved from git and that the .gitignore file is up
        to date.
        
        Args:
            force(Bool): In case of dependency conflict force syncing to first found branch
        """
        self.context.console.write_line('Updating workspace')

        package_set = self.__package_set

        # check for conflicted dependencies     
        if package_set.has_conflicts():
            if force:
                log('Forcing update')
                for project, refs in six.iteritems(package_set.conflicted_dependencies()):
                    log('  %s will use %s' % (project, str(refs[0])))
            else:
                log('FAILED : There are conflicted dependencies')
                log('   use --force to update anyway using first dependency') 
                log('')
                print_conflicts(package_set.conflicted_dependencies())
                return False

        self.context.console.start_task('Updating packages')
        package_set.update_package_versions(force=force, preview=preview)
        self.context.console.end_task()
        return True

    def verify(self):
        """ Check that the workspace appears to be valid."""     
        for worskpace_file in [self.context.workspace_info_filename]:
            if not os.path.exists(os.path.join(self.root_dir, worskpace_file)):
                return False
        return True
        
    def update_git_ignore_file(self, dependencies):
        """ Update the .gitignore file for this workspace to include all dependencies """     
        path = os.path.join(self.root_dir, '.gitignore')
        
        # read existing file
        gi_file = open(path, 'r')
        lines = gi_file.readlines()
        gi_file.close()
        
        # write all lines up to system marker line then append dependencies folders
        gi_file = open(path, 'w+')
        for line in lines:
            if line != '# ignore embedded hub libraries\n':
                gi_file.write(line)
            else:
                break
            
        gi_file.write('# ignore embedded hub libraries\n')
        for dep in dependencies:
            gi_file.write(dep.name + '/*\n')
        gi_file.close()
               
    def status(self, detailed=False, raw=False):       
        """
        Print the current status of the workspace to stdout. By default prints simple status 
        of state of dependent projects, either modified or unmodified.
        
        Args:
            detailed(Bool) : Display status of each dependent project as well.
        """         
        self.__package_set.print_status(detailed=detailed, raw=raw)        

    def get_workspace_info_path(self):
        """
        Get the path to the workspace info file
        
        Returns:
            string : Path to dependency file
        """
        return os.path.join(self.root_dir, self.context.workspace_info_filename)                        
                            
                
    def foreach(self, args):
        """
        Execute a process in the root of all dependent projects
        
        Args:
            args(list) : Argument list to use. i.e. ['git', 'status']
        """  
        # root = self.get_dependency_graph(refresh=False)
        # deps = root.flatten_dependencies()
        # for child in deps:
        #     cmd = args
        #     cwd = os.path.join(self.root_dir, child.name)
        #     process = subprocess.Popen(cmd, cwd=cwd)
        #     process.wait()
        
    def show_branches(self):
        """
        Print list of all dependent projects and which branch they are using to stdout.
        """
        for binding in self.__package_set.get_package_bindings():
            print('%-16s -> %s' % (binding.display_name(), 
                                   binding.local_filesystem_status().get_version()))
        

    def print_depends(self, refresh=False):
        """
        Print dependency information to stdout. This includes.
            List of all dependent projects and which branch they use
            Dependency graph
            Dependency conflicts if they exist
        
        Args:
            refresh(Bool) : True to refresh dependencies from the network (this may be slow)
        """     
        # build dependency graph and check for conflicts
        self.__package_set.print_depends()

    def print_versions(self):
        log_banner("Workspace")
        deps = self.__package_set.get_flattened_dependencies()
        for dep in deps:
            log("%s : %s" % (dep.name, dep.branch))
        log("")
        log_banner("Local")
        bindings = self.__package_set.get_package_bindings()
        for binding in bindings:
            status = binding.local_filesystem_status()
            status_msg = status.get_version()
            if not status.is_installed():
                status_msg = "<missing>"
            log("%s : %s" % (binding.display_name(), status_msg))
                
    def import_project(self):
        """
        Import a hub project into this workspace. Will interactively query the user for project 
        and branch name and update the workspace dependency file.
        """             
        # hub = TheHub(self)

        # # get existing dependencies     
        # depends_path = self.get_workspace_info_path()
        # dep_file = Dependency.create_from_file(depends_path)
        # if not dep_file:
        #     return
        
        # # select repo and branch to import
        # hub_import = hub.select_import(existing_deps=dep_file)
        
        # if hub_import == None:
        #     return
        
        # project = hub_import[0]
        # branch = hub_import[1]
        # print ''
        # print 'Selected %s:%s' % (project.name, branch.name)
        
        # # add to workspace dependency file
        # print 'Writing ' + depends_path        
        # dep_file.add_child(Dependency('hub', project.name, branch.name))
        # dep_file.save_to_file(depends_path)
                        
        
    def get_root_dependency(self):
        """ Get the projects this workspace depends on """
        return self.__package_set.get_root_dependency()

    @staticmethod
    def add_command_line_options(parser):
        """
        Add all command line arguments to the main parser. 
        """
        parser.set_defaults(mode='workspace')
        subparsers = parser.add_subparsers()
        
        # init action
        add_command_line_action(subparsers, 'init', action_help='Initialize a new workspace')

        # update action
        update = add_command_line_action(subparsers, 'update', 
                                         action_help='Update all libraries in the workspace')

        update.add_argument('--refresh', '-r', action='store_true', 
                            help='Refresh dependencies. By default dependent repositories ' \
                                        'are not updated before dependency checking.')   

        update.add_argument('--force', '-f', action='store_true', 
                            help='Force updating all dependencies even if there is a conflict')
        update.add_argument('--preview', '-p', action='store_true', 
                            help='Do not update, just display what would happen if you did')

        # depends action        
        depends = add_command_line_action(subparsers, 'depends', 
                                          action_help=
                                          'Show dependency information for this workspace')

        depends.add_argument('--refresh', '-r', action='store_true', 
                             help='Refresh dependencies. By default dependent ' \
                             'repositories are not updated before dependency checking.')

        depends.add_argument('--force', '-f', action='store_true', 
                             help='Force updating all dependencies')

        # delete action
        add_command_line_action(subparsers, 'delete', action_help='Delete the workspace')
        
        # status action
        status = add_command_line_action(subparsers, 'status', 
                                         action_help=
                                         'Show status of all repositories in the workspace')
        status.add_argument('--detailed', '-d', 
                            action='store_true', 
                            help='Show detailed status of all repositories in the workspace')
        status.add_argument('--raw', '-r', 
                            action='store_true', 
                            help='Show raw output from underlying provider of all repositories' \
                                 ' in the workspace')
        
        
        # versions action
        add_command_line_action(subparsers, 'versions', 
                                action_help='Print the projects and versions this' \
                                             ' workspace depends on')

        # verify action
        add_command_line_action(subparsers, 'verify', 
                                action_help='Verify that the workspace appears correct')
        
        # foreach action
        foreach = add_command_line_action(subparsers, 'foreach', 
                                          action_help='Execute the remainder of the command line' \
                                                    ' within each dependent library\'s repository')
        foreach.add_argument('args', nargs=argparse.REMAINDER)
        
        # show command
        show = add_command_line_action(subparsers, 'show', 
                                       action_help='Display information about this workspace. ' \
                                       'Use \'tyworkspace.py show -h\' for more options')

        show_subparsers = show.add_subparsers()
        add_command_line_action(show_subparsers, 'branches', 
                                action_help='Show which branches are currently in the workspace', 
                                subaction=True)     
        
        # import command
        imp = add_command_line_action(subparsers, 'import', 
                                      action_help='Import a project into the current workspace')
        imp.add_argument('--sandbox', '-r', 
                         action='store_true', help='Include sandbox libraries in the output')                


            

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
