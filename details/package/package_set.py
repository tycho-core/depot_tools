#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Tuesday, 09 December 2014 01:07:11 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
from details.depends import Dependency, print_conflicts
from details.package.package_binding import PackageBinding
from details.utils.misc import log, log_banner, vlog

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class PackageSet(object):
    """ Set of all packages mapped into the the workspace """
    
    def __init__(self, context):
        """ Constructor """
        self.__context = context
        self.__root_dependency = None
        self.__flattened_dependencies = None
        self.__packages = []
        self.__package_bindings = []
        self.__conflicted_dependencies = None

    @staticmethod
    def create_from_dependency(context, root_dep, refresh_dependencies):
        """ Create a package set from root dependency """
        dset = PackageSet(context)
        dset.set_root_dependency(root_dep, refresh_dependencies)
        return dset

    @staticmethod
    def create_from_dependency_string(context, in_str, refresh_dependencies=True):
        """ Create a package set from a dependency string """
        dep = Dependency.create_from_string(in_str)
        return PackageSet.create_from_dependency(context, dep, refresh_dependencies)

    @staticmethod
    def create_from_dependency_file(context, file_path, refresh_dependencies=True):
        """ Create a package set from a dependency file """
        dep = Dependency.create_from_file(file_path)
        return PackageSet.create_from_dependency(context, dep, refresh_dependencies)

    def set_root_dependency(self, root_dep, refresh_dependencies=True):
        """ Set the root dependencies """
        self.__root_dependency = root_dep
        self.__build_dependency_graph(refresh_dependencies)

    def get_root_dependency(self):
        """ Get the root of the dependency graph for this set """
        return self.__root_dependency

    def get_flattened_dependencies(self):
        """ Get a flat list of projects this set depends on """
        return self.__flattened_dependencies

    def has_conflicts(self):
        """ Returns true if this package set has conflicted dependencies """
        return len(self.__conflicted_dependencies) > 0

    def conflicted_dependencies(self):
        """ Returns conflicted dependencies """
        return self.__conflicted_dependencies()

    def print_depends(self):
        """ Print dependency chain to stdout """
        self.__root_dependency.print_depends()

    def print_status(self, detailed=False, raw=False):
        """
        Print the current status of the workspace to stdout. By default prints simple status 
        of state of dependent projects, either modified or unmodified.
        
        Args:
            detailed(Bool) : Display status of each dependent project as well.
        """         
        #get top level dependencies
        conflicted_deps = self.__conflicted_dependencies
                
        # status of all packaged in local filesystem
        pkg_status = [pkg.local_filesystem_status() for pkg in self.__package_bindings]

        # print summary of status of each package
        log_banner('Dependencies repository state')
        for status, binding in zip(pkg_status, self.__package_bindings):
            mod_str = 'modified'
            if status.is_clean():
                mod_str = 'unmodified'
            log('%-16s -> %-10s : %s' % (str(binding.package), status.get_version(), mod_str))

        if detailed:
            all_clean = True
            if not raw:
                log('')
                log_banner('Modifications')
            for status, binding in zip(pkg_status, self.__package_bindings):
                if not status.is_clean():
                    log('')
                    if raw:
                        log_banner(binding.package.name)
                        log(status.get_raw_modifications())
                    else:
                        mods = status.get_modifications()
                        for mod in mods:
                            log('%s : %s : %s' % (binding.package.name, 
                                                  mod.pretty_code_name(), 
                                                  mod.path()))
                    log('')
                    all_clean = False
                    
            if all_clean:
                log('All dependencies are unmodified')
                
            
        if len(conflicted_deps) > 0:
            log('')
            log_banner('Conflicts')
            print_conflicts(conflicted_deps)
            log('')
            
            log('NOT OK - There are conflicted dependencies')

    def bind_packages(self, mappings, refresh_dependencies=True): 
        """ Creates the bindings for all packages to the local filesystem """
        for pkg in self.__packages:
            info = pkg.get_package_info(refresh_dependencies)
            pkg_dir = '%s/%s' % (info.get_workspace_mapping(), pkg.name)                    
            pkg_dir = mappings.apply_templates(pkg_dir)
            pkg_dir = os.path.abspath(pkg_dir)
            self.__package_bindings.append(PackageBinding(pkg, pkg_dir))

    def update_package_versions(self, force=False, preview=False):
        """ Ensure the local working copy versions correspond to workspace versions.
        Packages that are not in the local workspace with be retrieved.
        Packages that are on the incorrect version will be updated to the correct version"""        
        for binding in self.__package_bindings:
            package = binding.package

            # track current dependency for error reporting
            self.__context.current_dependency = package.dependency

            # get current package status
            status = binding.local_filesystem_status()
            local_version = status.get_version()
            desired_version = package.version

            if not status.is_installed():
                if preview:
                    log("%s not installed, would be checked out." % str(package))
                else:
                    binding.checkout()                    
            elif local_version != desired_version:
                if preview:
                    if status.is_modified():
                        log("%s is modified, requires --force to update from '%s' to version '%s'" %
                            (package.name, local_version, desired_version))
                    else:
                        log("%s-%s would be updated to '%s'" % (package.name, 
                                                                local_version, 
                                                                desired_version))
                else:
                    if binding.change_version(force=force):
                        log("Changed %s from version '%s' to '%s'" % (package.name, 
                                                                      local_version, 
                                                                      desired_version))
                    else:
                        log("Failed to change %s from version '%s' to '%s'" % (package.name, 
                                                                               local_version, 
                                                                               desired_version))
            # track current dependency for error reporting
            self.__context.current_dependency = None


    def update_packages(self):
        """ Update all packages. This will install them if not present and ensure they are 
        up to date if the are """
        log('Updating packages')
        for pkg in self.__package_bindings:
            # track current dependency for error reporting
            self.__context.current_dependency = pkg.package.dependency

            if pkg.is_installed():
                log('    Updating %s...' % (pkg.display_name()))
                pkg.update()
            else:
                log('    Checking out %s...' % (pkg.display_name()))
                pkg.checkout()

            # track current dependency for error reporting
            self.__context.current_dependency = None

    def get_package_bindings(self):
        """ Returns the local bindings for this package set. """
        return self.__package_bindings
        
    def __build_dependency_graph(self, refresh_dependencies):
        """ Get full graph of dependencies for this set of packages """
        package_map = {}

        def get_dep(dep):
            """ Retrieve package dependencies """
            # track current dependency for error reporting
            self.__context.current_dependency = dep

            pkg = self.__context.package_manager.get_package(dep.source, dep.name, dep.branch,
                                                             refresh_dependencies)
            dep = pkg.get_dependencies(refresh_dependencies)
            #dep.package = pkg
            package_map[str(dep)] = pkg

            # track current dependency for error reporting
            self.__context.current_dependency = None

            return dep

        # build the dependency graph
        self.__root_dependency.build_dependency_graph(refresh=False, dep_func=get_dep)
        self.__flattened_dependencies = self.__root_dependency.flatten_dependencies()
        vlog(self.__flattened_dependencies)
        for dep in self.__flattened_dependencies:
            # track current dependency for error reporting
            self.__context.current_dependency = dep

            pkg = self.__context.package_manager.get_package(dep.source, dep.name, dep.branch)
            pkg.dependency = dep
            self.__packages.append(pkg)

            # track current dependency for error reporting
            self.__context.current_dependency = None

        # check for package conflicts
        self.__conflicted_dependencies = self.__root_dependency.get_dependency_conflicts()


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
