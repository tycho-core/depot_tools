#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 11:04:58 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function
import os
import os.path
import argparse
import subprocess
import json
import six
from details.depends import print_conflicts, Dependency
from details.utils.misc import fatal_error, log, add_command_line_action, log_banner
from details.utils.misc import dict_value_or_none
from details.utils.file import  get_directory_tree
from details.scm.git.thehub import TheHub
from details.template import Template
from details.templateengine import TemplateEngine
from details.workspace_mapping import WorkspaceMapping
from details.package.package_manager import PackageManager
from details.package.package_set import PackageSet
from details.workspace_info import WorkspaceInfo
from details.package.provider_query_interface import InteractiveQueryInterface
from details.processors.cmake_build_processor import CMakeBuildProcessor

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Workspace(object):
    """ Object representing the current workspace."""

    def __init__(self, context, root_dir, check_valid=True, refresh_dependencies=True):
        """ Constructor """

        # root directory of the workspace
        self.root_dir = root_dir

        # execution context information
        self.context = context
        self.__package_set = None
        self.__mappings = None
        self.__info = None

        if not context.options.quiet:
            context.console.write_line('Initialising workspace')

        # load workspace info file and setup mappings
        self.__info = WorkspaceInfo.create_from_json_file(self.get_workspace_info_path())


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

        context.console.start_task('Processing dependencies')
        self.__package_set = PackageSet.create_from_dependency(self.context,
                                                               mappings,
                                                               self.__info.get_dependencies(),
                                                               check_valid, refresh_dependencies)
        context.console.end_task()


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

    def get_root_dir(self):
        """ Get the path to the root of this workspace """
        return self.root_dir

    def get_filesystem_mappings(self):
        """ Get the workspace file system mappings """
        return self.__mappings

    def update(self, force=False, preview=False):
        """
        Update the workspace in the passed directory. This will ensure that all
        dependencies have been retrieved from git and that the .gitignore file is up
        to date.

        Args:
            force(Bool): In case of dependency conflict force syncing to first found branch
        """
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

        # update all the packages
        self.context.console.start_task('Updating packages')
        package_set.update_package_versions(force=force, preview=preview)
        self.context.console.end_task()

        # generate cmake files
        self.context.console.start_task("Process CMake")
        cmake = CMakeBuildProcessor(self.context)
        cmake.process(self, self.__package_set)
        cmake.write_cmake_file(os.path.join(self.root_dir, self.context.local_workspace_cmake_filename))
        self.context.console.end_task()

        # save current workspace state
        self.save_local_workspace_info()

        return True

    def get_local_workspace_info_path(self):
        """ Returns the path to the local workspace info file """
        return os.path.join(self.root_dir, self.context.local_workspace_info_filename)

    def save_local_workspace_info(self):
        """ Save the current state of the workspace. This includes information
            on the mappings of projects into the workspace
        """
        local_info = self.__info.clone()

        local_pkg_bindings = []
        for binding in self.__package_set.get_package_bindings():
            package = binding.get_package()
            relpath = os.path.relpath(binding.get_package_root_dir(), self.root_dir)
            pkg_name = '%s:%s:%s' % (package.provider.source_name, package.name, package.version)
            local_pkg_bindings.append({
                'project' : pkg_name,
                'local_dir' : relpath,
                'status' : 'unknown'
                })
        local_info.set_package_bindings(local_pkg_bindings)
        local_info.save_to_json_file(self.get_local_workspace_info_path())

    def load_local_workspace_info(self):
        """ Load the current state of the workspace """
        path = self.get_local_workspace_info_path()
        if not os.path.exists(path):
            return None

        return WorkspaceInfo.create_from_json_file(path)

    def verify(self):
        """ Check that the workspace appears to be valid."""
        self.context.console.start_task('Verifying workspace')
        for worskpace_file in [self.context.workspace_info_filename]:
            if not os.path.exists(os.path.join(self.root_dir, worskpace_file)):
                return False

        pkg_status = []

        workspace_corrupted = False

        # constants for describing current state of workspace packages
        PkgDoesNotExistInProvider = 1
        PkgPristine = 2
        PkgModified = 3
        PkgCorrupted = 4
        PkgDoesNotExistLocally = 5
        PkgIncorrectVerson = 6

        local_info = self.load_local_workspace_info()
        if local_info:
            # check that the packages are intact
            for binding in local_info.get_package_bindings():
                local_dir = dict_value_or_none(binding, 'local_dir')
                project = dict_value_or_none(binding, 'project')
                status = dict_value_or_none(binding, 'status')

                if not local_dir:
                    workspace_corrupted = True
                    break

                if not project:
                    workspace_corrupted = True
                    break

                # query provider about the status of the package
                dep = Dependency.create_from_string(project).children[0]
                pkg = self.context.package_manager.get_package(dep.source, dep.name, dep.branch)

                if not pkg:
                    # package does not exist anymore
                    pkg_status.append([
                        PkgDoesNotExistInProvider,
                        "Package '%s' not longer exists in provider '%s'" % (str(pkg),
                                                                             pkg.provider.source_name)
                        ])
                else:
                    local_status = pkg.local_filesystem_status(os.path.join(self.root_dir, local_dir))

                    if not local_status.is_installed():
                        pkg_status.append([
                            PkgDoesNotExistLocally,
                            "Package '%s' is not installed locally" % (str(pkg))
                            ])
                    elif not local_status.is_valid():
                        pkg_status.append([
                            PkgCorrupted,
                            "Package '%s' is corrupted locally" % (str(pkg))
                            ])
                    elif local_status.is_modified():
                        pkg_status.append([
                            PkgModified,
                            "Package '%s' has been locally modified" % (str(pkg))
                            ])
                    elif local_status.get_version() != dep.branch:
                        pkg_status.append([
                            PkgIncorrectVerson,
                            "Package '%s' is using locally using the incorrect version" % (str(pkg))
                            ])
                    else:
                        pkg_status.append([
                            PkgPristine,
                            "Package '%s' is in a pristine state" % (str(pkg))
                            ])

        self.context.console.end_task()

        # print report
        for status in pkg_status:
            print(status[1])

        return not workspace_corrupted

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


    def foreach(self, provider, args):
        """
        Execute a process in the root of all dependent projects

        Args:
            provider(string) : Provider type to run the command for or None for all.
            args(list)       : Argument list to use. i.e. ['git', 'status']
        """
        if len(args) == 0:
            return
        from utils.misc import execute
        results = []
        console = self.context.console
        task_name = ' '.join(args)
        console.start_task(task_name)
        for binding in self.__package_set.get_package_bindings():
            if provider is not None and provider != binding.get_package().provider.name:
                continue
            console.update_task(binding.get_package().name)
            results.append((binding, execute(args[0], binding.get_package_root_dir(), args[1:], capture=True)))
        console.end_task()

        # display report
        for result in results:
            console.write_line('---------------------------------------------------')
            console.write_line(task_name + ' - ' + result[0].get_package().name)
            console.write_line('---------------------------------------------------')
            console.write_line(result[1][1])
            if result[1][0] != 0:
                console.write_line('FAILED')



    def show_branches(self):
        """
        Print list of all dependent projects and which branch they are using to stdout.
        """
        for binding in self.__package_set.get_package_bindings():
            print('%-16s -> %s' % (binding.display_name(),
                                   binding.local_filesystem_status().get_version()))


    def get_depends_info(self):
        """ Get dependency information in simple structure suitable for
        dumping as json """
        return self.__package_set.get_depends_info()

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

    def get_available_imports(self):
        """
        Get a list of all projects available to import from the hub
        """
        query_interface = self.context.package_manager.get_aggregated_query_interface()
        projects = query_interface.get_projects()
        existing_deps = self.__package_set.get_root_dependency()
        results = []
        for project in projects:
            pdict = {}
            pdict['provider'] = project.get_owner().get_provider().source_name
            pdict['name'] = project.get_display_name()
            pdict['existing'] = existing_deps.project_exists(project.get_display_name())
            pdict['versions'] = [ version.get_display_name() for version in project.get_versions()]
            results.append(pdict)

        return results

    def import_project_by_name(self, provider, name, version):
        """ Import a project by name to the workspace """
        # add to workspace info file
        info_path = self.get_workspace_info_path()
        info = WorkspaceInfo.create_from_json_file(info_path)
        info.add_dependency(Dependency(provider, name, version))
        if not self.context.options.quiet:
            self.context.console.write_line('Writing ' + info_path)
        info.save_to_json_file(info_path)

    def import_project(self):
        """
        Import a hub project into this workspace. Will interactively query the user for project
        and branch name and update the workspace dependency file.
        """
        query_interface = self.context.package_manager.get_aggregated_query_interface()
        interactive_interface = InteractiveQueryInterface(query_interface)

        # get existing dependencies
        existing_deps = self.__package_set.get_root_dependency()

        # select project and version to import
        hub_import = interactive_interface.select_import(existing_deps=existing_deps)

        if hub_import is None:
            return

        project = hub_import[0]
        version = hub_import[1]
        provider = project.get_owner().get_provider()
        self.context.console.write_line('Selected %s:%s:%s' % (provider.source_name, project.get_display_name(), version.get_display_name()))

        # add to workspace info file
        self.import_project_by_name(provider.source_name,
                                    project.get_display_name(),
                                    version.get_display_name())


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

        def add_common_flags(command):
            command.add_argument('--refresh', '-r', action='store_true',
                                help='Refresh dependencies. By default dependent repositories ' \
                                'are not updated before dependency checking.')

            command.add_argument('--validate', '-v', action='store_true',
                                 help='Check dependenices are valid by querying the remote, ' \
                                 'this can be slow.')

        # init action
        init = add_command_line_action(subparsers, 'init', action_help='Initialize a new workspace')
        add_common_flags(init)
        # update action
        update = add_command_line_action(subparsers, 'update',
                                         action_help='Update all libraries in the workspace')
        add_common_flags(update)

        update.add_argument('--force', '-f', action='store_true',
                            help='Force updating all dependencies even if there is a conflict')
        update.add_argument('--preview', '-p', action='store_true',
                            help='Do not update, just display what would happen if you did')

        # depends action
        depends = add_command_line_action(subparsers, 'depends',
                                          action_help=
                                          'Show dependency information for this workspace')
        add_common_flags(depends)

        depends.add_argument('--force', '-f', action='store_true',
                             help='Force updating all dependencies')

        # delete action
        add_command_line_action(subparsers, 'delete', action_help='Delete the workspace')

        # status action
        status = add_command_line_action(subparsers, 'status',
                                         action_help=
                                         'Show status of all repositories in the workspace')
        add_common_flags(status)
        status.add_argument('--detailed', '-d',
                            action='store_true',
                            help='Show detailed status of all repositories in the workspace')
        status.add_argument('--raw', '-R',
                            action='store_true',
                            help='Show raw output from underlying provider of all repositories' \
                                 ' in the workspace')


        # versions action
        versions = add_command_line_action(subparsers, 'versions',
                                action_help='Print the projects and versions this' \
                                             ' workspace depends on')

        add_common_flags(versions)

        # verify action
        verify = add_command_line_action(subparsers, 'verify',
                                action_help='Verify that the workspace appears correct')
        add_common_flags(verify)

        # foreach action
        foreach = add_command_line_action(subparsers, 'foreach',
                                          action_help='Execute the remainder of the command line' \
                                                    ' within each dependent library\'s repository')
        add_common_flags(foreach)
        foreach.add_argument('--provider', '-p',
                             action='store', help='Provider type to execute for, one of [git, http]')
        foreach.add_argument('args', nargs=argparse.REMAINDER)

        # show command
        show = add_command_line_action(subparsers, 'show',
                                       action_help='Display information about this workspace. ' \
                                       'Use \'tyworkspace.py show -h\' for more options')

        add_common_flags(show)
        show_subparsers = show.add_subparsers()
        add_command_line_action(show_subparsers, 'branches',
                                action_help='Show which branches are currently in the workspace',
                                subaction=True)
        add_command_line_action(show_subparsers, 'imports',
                                action_help='Show which imports are available for the workspace',
                                subaction=True)

        # import command
        imp = add_command_line_action(subparsers, 'import',
                                      action_help='Import a project into the current workspace')
        add_common_flags(imp)
        imp.add_argument('--sandbox', '-s',
                         action='store_true', help='Include sandbox libraries in the output')
        imp.add_argument('--project', '-p',
                         action='store', help='Project to import in <provider>:<name>:<version> format')
        imp.add_argument('--update', '-u',
                         action='store_true', help='Update the workspace after importing')




#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
