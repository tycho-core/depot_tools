#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 04 December 2014 10:20:28 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest
import textwrap
import os
from details.depends import Dependency
from details.test_case import TestCase

#-----------------------------------------------------------------------------
# Unit Tests
#-----------------------------------------------------------------------------

class TestDependency(TestCase):
    __test_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

    def test_construct(self):
        dep = Dependency('hub', 'tiger', 'bitey_branch')
        self.assertEqual(dep.source, 'hub')
        self.assertEqual(dep.name, 'tiger')
        self.assertEqual(dep.branch, 'bitey_branch')
        self.assertIsNone(dep.parent)
        self.assertEqual(len(dep.children), 0)

    def test_create_string(self):
        test_str = """
            hub:project1:branch1
            sandbox:project2:branch2
        """

        dep = Dependency.create_from_string(textwrap.dedent(test_str))
        self.assertIsNotNone(dep)
        self.assertEquals(len(dep.children), 2)
        self.assertTrue(dep.contains(Dependency('hub', 'project1', 'branch1')))
        self.assertTrue(dep.contains(Dependency('sandbox', 'project2', 'branch2')))

        new_dep = Dependency('hub', 'project3', 'branch3')
        dep.add_child(new_dep)
        self.assertTrue(dep.contains(new_dep))
        self.assertEquals(len(dep.children), 3)
        self.assertEquals(new_dep.parent, dep)

    def test_create_from_list(self):
        test_data = [
            'hub:project1:branch1',
            'sandbox:project2:branch2'
        ]

        dep = Dependency.create_from_list(test_data)
        self.assertIsNotNone(dep)
        self.assertEquals(len(dep.children), 2)
        self.assertTrue(dep.contains(Dependency('hub', 'project1', 'branch1')))
        self.assertTrue(dep.contains(Dependency('sandbox', 'project2', 'branch2')))


    def test_create_file(self):
        dep = Dependency.create_from_file(os.path.join(TestDependency.__test_data_path, 
                                                       'test_dep.txt'))
        self.assertIsNotNone(dep)
        self.assertEquals(len(dep.children), 2)
        self.assertTrue(dep.contains(Dependency('hub', 'project1', 'branch1')))
        self.assertTrue(dep.contains(Dependency('sandbox', 'project2', 'branch2')))


    def test_graph(self):
        graph = {
            'hub' : {
                'project1_branch1' : """
                hub:project2:branch2
                """,

                'project2_branch2' : """
                hub:project3:branch1
                """,

                'project3_branch1' : """
                """
            }
        }
        dep = Dependency.create_from_string(graph['hub']['project1_branch1'])
        self.assertIsNotNone(dep)
        self.assertEquals(len(dep.children), 1)

        def get_dep(dep):
            """ dependency lookup """
            name = '%s_%s' % (dep.name, dep.branch)
            return Dependency.create_from_string(graph[dep.source][name])

        dep.build_dependency_graph(refresh=False, dep_func=get_dep)
        self.assertEquals(len(dep.children), 1)
        child1 = dep.children[0]
        self.assertEquals(len(child1.children), 1)
        self.assertTrue(child1.parent is dep)

        child2 = child1.children[0]
        self.assertEquals(len(child2.children), 0)
        self.assertTrue(child2.parent is child1)
        self.assertTrue(child2.tree_contains(child1))
        self.assertFalse(child2.tree_contains(Dependency('hub', 'project51', 'branch1')))

        # test graph flattening
        flat_graph = dep.flatten_dependencies()
        self.assertEquals(len(flat_graph), 2)
        


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
