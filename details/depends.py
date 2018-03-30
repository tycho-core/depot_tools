#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Wednesday, 10 December 2014 10:28:08 AM
#-----------------------------------------------------------------------------

#TODO : rewrite print_depends using get_depends_info results
#TODO : add conflict information to get_depends_info results

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function
import os
import re
import sys
import six
from details.utils.misc import log, vlog, log_banner, indent

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------


class CircularDependencyException(Exception):
    def __init__(self, dep1, dep2):
        msg = "Circular dependency detected %s -> %s -> %s" % (str(dep1), str(dep2), str(dep1))
        super(CircularDependencyException, self).__init__(msg)

class Dependency(object):
    """ Node in the dependency heirarchy """

    # identifies the root of the heirarchy
    SourceRoot = 'root'

    # regex for parsing dependency strings
    __regex = r'(?P<src>\w+):(?P<project>\w+):(?P<version>[\w\-\.]+)'

    @staticmethod
    def create_root():
        """ Create a root dependency """
        return Dependency(Dependency.SourceRoot, Dependency.SourceRoot,
                          Dependency.SourceRoot)

    @staticmethod
    def create_from_string(in_str):
        """ Create Dependency() object from string """
        matches = re.findall(Dependency.__regex, in_str)
        dependencies = Dependency.create_root()
        for match in matches:
            obj = Dependency(match[0], match[1], match[2])
            dependencies.add_child(obj)

        return dependencies

    @staticmethod
    def create_from_list(in_list):
        """ create Dependency() object from list of strings """
        dependencies = Dependency.create_root()
        for string in in_list:
            match = re.match(Dependency.__regex, string)
            if match:
                obj = Dependency(match.group('src'), match.group('project'), match.group('version'))
                dependencies.add_child(obj)

        return dependencies


    @staticmethod
    def create_from_file(path, suppress_error_msg=False):
        """ Load dependencies from a file """
        if not os.path.exists(path):
            if not suppress_error_msg:
                log("Error: Create Dependencies: Could not locate file '%s'" % path)
            return None
        # load the dependency file and pass library and branch info
        dep_file = open(path, 'r')
        lines = dep_file.read()
        dep_file.close()
        return Dependency.create_from_string(lines)

    def __init__(self, source, name, branch):
        """ Constructor """
        # either 'hub' or 'sandbox'
        self.source = source
        # repository name
        self.name = name
        # branch name 
        self.branch = branch
        # parent dependency
        self.parent = None
        # child dependencies
        self.children = []
        
    def save_to_file(self, path):
        """ Save dependencies to a file """
        dep_file = open(path, 'w')
        for dep_file in self.children:
            dep_file.write('%s\n'  % (dep_file))
        dep_file.close()

    def __repr__(self):
        """ Returns string representation of the dependency """
        return ('%s:%s:%s') % (self.source, self.name, self.branch)
    
    def __eq__(self, other):
        """ Return True if dependency is identical to other """
        if other is None:
            return False
        return (self.name == other.name and 
                self.source == other.source and self.branch == other.branch)

    def __ne__(self, other):
        """ False True if dependency is not equal to other """
        return not self == other

    def __hash__(self):
        """ Returns Hash of the dependency """
        return hash(str(self))

    def contains(self, test_dep):
        """ Returns true if this dependency contains the passed dependency """
        for child in self.children:
            if child == test_dep:
                return True
        return False

    def tree_contains(self, test_dep):
        """ Returns true if the passed dependency exists anywhere in the tree of
        dependencies"""
        cur = self
        while cur != None:
            if cur.contains(test_dep):
                return cur
            cur = cur.parent
        return None

    def parent_path_contains(self, test_dep):
        """ Checks if dependency exists anywhere on the direct route from this dependency to the
        root. If it does it returns the parent of the dependency otherwise None."""
        cur = self.parent
        while cur != None:
            if cur == test_dep:
                return cur.parent
            cur = cur.parent
        return None

    def contains_project(self, name):
        """ Returns true if this dependency contains a project of the passed name """
        for child in self.children:
            if child.name == name:
                return True
        return False

    def add_child(self, new_child):
        """ Add a node as a child of this dependency. """
        for child in self.children:
            if child == new_child:
                return
        self.children.append(new_child)
        new_child.parent = self

    def project_exists(self, name):
        """Return true if the project is already a dependency"""
        for dep in self.children:
            if dep.name == name:
                return True
            
        return False

    def get_root_dependency(self):
        """
        Retrieve the root of this dependency chain

        Returns:
            Dependency()
        """

        node = self
        while node != None and node.parent != None:
            node = node.parent

        return node 

    def get_dependency_chain(self):
        """
        Returns a list of all dependencies in the chain from this dependency to the root

        Returns:
            list(Dependency)
        """

        chain = []
        node = self
        while node != None:
            chain.insert(0, node)
            node = node.parent

        return chain

    def flatten_dependencies_by_name(self):
        """
        Build a dictionary of all library dependencies by name
        
            Args:
                root(Dependency) : Root dependency object
                
            Returns:
                dictionary::
                    {
                        'name' : [ Dependency(), Dependency() ]
                    }
                    
        """

        name_dict = {}
        for node in self.children:
            self.__flatten_dependencies_aux(name_dict, node)
        return name_dict

    
    def flatten_dependencies(self):
        """
        Return:
            list: List of depends.Dependency objects.
            
        Note:
            In case of a conflict (multiple referenced branches) it will include the first
            one found 
        """
        flattened_deps_by_name = self.flatten_dependencies_by_name()
        dependencies = []
        for _, refs in flattened_deps_by_name.iteritems():
            for ref in refs:
                if not ref in dependencies:
                    dependencies.append(ref)
                    continue
        return dependencies
                
    def __flatten_dependencies_aux(self, name_dict, node):
        """
        Helper function for Workspace.flatten_dependencies
        """             
        if node.name in name_dict:
            name_dict[node.name].append(node)
        else:
            name_dict[node.name] = [node]
            
        for child in node.children:
            self.__flatten_dependencies_aux(name_dict, child)        

    def get_dependency_conflicts(self):
        """
        Build a dictionary by name of all library dependencies that refer to multiple 
        project branches.

        Args:
            root(Dependency) : Root dependency object
            
        Returns:
            dictionary::
                {
                    'name' : [ Dependency(), Dependency() ]
                }               
        """
        conflicts = {}
        projects = self.flatten_dependencies_by_name()
        
        # check that under each library all uses reference the same source and branch
        for project, refs in projects.iteritems():
            match = None
                
            for ref in refs:
                if match == None:
                    match = ref
                    continue
                else:
                    if match != ref:
                        conflicts[project] = refs
                        break
    
        return conflicts

    def print_dependencies(self, node=None, depth=0):
        """
        Print dependency graph to stdout.
        
        Args:
            node(tydepends.Dependency) : Root dependency
            depth(int) : traversal depth
        """
        if node == None:
            node = self

        log(node, tabs=depth)
        for child in node.children:
            self.print_dependencies(child, depth=depth + 1)

    def print_depends(self):
        """
        Print dependency information to stdout. This includes.
            List of all dependent projects and which branch they use
            Dependency graph
            Dependency conflicts if they exist
        
        Args:
            refresh(Bool)  : True to refresh dependencies from the network (this may be slow)
        """
        # build dependency graph and check for conflicts
        flattened_deps = self.flatten_dependencies_by_name()
        conflicted_deps = self.get_dependency_conflicts()

        
        # print list of all dependent projects
        log_banner('Dependent projects')
        for project, refs in flattened_deps.iteritems():
            visited_deps = set()
            branches = ""
            for ref in refs:
                if not ref in visited_deps:
                    if len(visited_deps) > 0:
                        branches = branches + ", "
                    branches = branches + str(ref)
                    visited_deps.add(ref)
            log('%-16s : %s' % (project, branches))

        log('')
        log_banner('Dependency graph')
        self.print_dependencies()

        if len(conflicted_deps) > 0:
            log('')
            log_banner('Conflicts')
            print_conflicts(conflicted_deps)
            log('')

            num_conflicts = len(conflicted_deps)
            msg = 'NOT OK - %s conflicted ' % (num_conflicts)
            if num_conflicts == 1:
                msg = msg + "dependency"
            else:
                msg = msg + "dependencies"
            log(msg)
        else:
            log('')
            log('OK - Conflict free dependencies')

    def get_depends_info(self):
        """
        Builds a simple structure containg dependency information suitable for dumping to json or printing. This includes.
            List of all dependent projects and which branch they use
            Dependency graph
            Dependency conflicts if they exist
        """
        output = {}

        # build dependency graph and check for conflicts
        flattened_deps = self.flatten_dependencies_by_name()
        conflicted_deps = self.get_dependency_conflicts()

        # get list of all dependent projects and the branches referenced
        output['depends'] = []
        for project, refs in flattened_deps.iteritems():
            visited_deps = set()
            branches = []
            for ref in refs:
                if not ref in visited_deps:
                    branches.append(str(ref))
                    visited_deps.add(ref)
            output['depends'].append({
                'name': str(project),
                'branches': branches
            })

        def enum_deps(parent, node):
            for child in node.children:
                entry = {
                    'source': child.source,
                    'name': child.name,
                    'branch': child.branch,
                    'children': []
                }
                parent['children'].append(entry)
                enum_deps(entry, child)

        output['graph'] = {
            'source': self.source,
            'name': self.name,
            'branch': self.branch,
            'children': []
        }
        enum_deps(output['graph'], self)

        output['conflicts'] = {
            'num': len(conflicted_deps),
            'entries': []
        }
#        if len(conflicted_deps) > 0:
#            print_conflicts(conflicted_deps)

        return output


    def build_dependency_graph(self, refresh=False, depth=0, dep_func=None):
        """
        Build the dependency graph for this dependency. This will burrow through all
        dependencies to create the full dependency graph for this dependency.

        Args:
            refresh(Bool) : True to update dependency info from the network.

        Returns:
             depends.Dependency() object
        """
        assert dep_func

        for cur_child in self.children:
            # get the dependencies of this child
            new_deps = dep_func(cur_child)

            for new_child in new_deps.children:
                # check for circular dependency
                enode = self.parent_path_contains(new_child)
                if enode:
                    raise CircularDependencyException(new_child, cur_child)
                cur_child.add_child(new_child)
                vlog('Adding child(%s) to parent(%s)' % (new_child, cur_child), tabs=depth)

            cur_child.build_dependency_graph(refresh=refresh, depth=depth+1, dep_func=dep_func)

        return self

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def print_conflicts(conflicted_deps):
    """ Print all dependency conflicts and their dependency chain to stdout """
    for project, refs in conflicted_deps.iteritems():
        branches = ""
        projects = ""
        first = True
        num_refs = len(refs)
        cur_ref = 0
        for ref in refs:
            if not first:
                if cur_ref == (num_refs-1):
                    projects = projects + ' and '
                    branches = branches + ' and '
                else:
                    projects = projects + ', '
                    branches = branches + ', '
            branches = branches + ref.branch

            if ref.parent.source == Dependency.SourceRoot:
                projects = projects + 'the workspace'
            else:
                projects = projects + ref.parent.name + ':' + ref.parent.branch
            first = False
            cur_ref = cur_ref + 1


        log('%s using branches %s due to %s\n' % (project, branches, projects))
        for ref in refs:
            # write out each reference from root to the reference
            chain = ref.get_dependency_chain()
            depth = 1
            for dep in chain:
                indent(depth)
                tail = ""
                if dep == ref:
                    tail = "   <---- Using branch " + dep.branch

                if dep.source == Dependency.SourceRoot:
                    log('Workspace')
                else:
                    log("%s:%s%s" % (dep.name, dep.branch, tail))
                depth = depth + 1
            log('')

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    print("File : " + sys.argv[1])
    dep = Dependency.create_from_file(sys.argv[1])
    if dep:
        print(dep.children)
    else:
        print('Could not load : ' + sys.argv[1])

if __name__ == "__main__":
    main()
