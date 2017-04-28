## -*- coding: utf-8 -*-
##
## tree.py
##
## Author:   Toke Høiland-Jørgensen (toke@toke.dk)
## Date:     26 April 2012
## Copyright (c) 2012, Toke Høiland-Jørgensen
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

class Tree(object):
    def __init__(self, tree):
        self.root = Node(tree[0], tree[1])
        self.add_level(self.root, tree[2])

    def add_level(self, parent, values):
        for value in values:
            node = parent.add_chield(value[0], value[1])
            self.add_level(node, value[2])

    def find_path(self, name, root=None):
        """Depth-first search to find the path to a node with a given name"""
        if root is None:
            root = self.root

        if root.name == name:
            return [root]

        if len(root.children) == 0:
            return None

        for child in root.children:
            found = self.find_path(name, child)
            if found is not None:
                return [root]+found

    def find_common_path(self, names):
        """Find common path between a set of nodes."""
        paths = []
        for name in names:
            path = self.find_path(name)
            if path is None:
                return None
            paths.append(path)
        common_path = []
        for i in range(min([len(p) for p in paths])):
            steps = [p[i] for p in paths]
            value = steps[0]
            for s in steps:
                if s != value:
                    return common_path
            common_path.append(value)
        return common_path

    def find_value(self, name):
        """Find the value for a name in the tree"""
        path = self.find_path(name)
        if path is None:
            return None
        return path[-1].value

    def find_common_value(self, names):
        """Find the value of the nearest common ancestor of a set of nodes"""
        path = self.find_common_path(names)
        if path is None:
            return None
        return path[-1].value


    def __repr__(self):
        return "<Tree: %s>" % self.root

class Node(object):

    def __init__(self, name, value, parent=None):
        self.name = name
        self.value = value
        self.parent = parent
        self.children = []

    def add_chield(self,name,value):
        n = Node(name,value, self)
        self.children.append(n)
        return n

    def __repr__(self):
        return "<Node: %s, %s>" % (self.name, self.value, ", ".join(map(repr,self.children)))


if __name__ == "__main__":
    tree = Tree(["root", 0.0, [["1", 0.5, [["1.1", 0.75, [["1.1.1", 0.9, []],
                                                          ["1.1.2", 0.92, []]]],
                                           ["1.2", 0.6, [["1.2.1", 0.9, []]]]]]]])
    print(tree)
    print([i.name for i in tree.find_path("1.1.2")])
    print(tree.find_value("1.2.1"))
    print([i.name for i in tree.find_common_path(["1.1.1", "1.1.2"])])
    print(tree.find_common_value(["1.1.1","1.2.1", "1.1.2"]))
