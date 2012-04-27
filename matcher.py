## -*- coding: utf-8 -*-
##
## matcher.py
##
## Author:   Toke Høiland-Jørgensen (toke@toke.dk)
## Date:     27 April 2012
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

class Matcher(object):
    _default_config = dict(retrieve=2)

    def __init__(self, cases=[]):
        self.cases = cases
        self.config = dict(self._default_config)

    def match(self, query):
        similarities = []
        for case in self.cases:
            similarities.append((query.similarity(case), case))
        similarities.sort()
        similarities.reverse()
        return similarities[:self.config['retrieve']]
