#!/usr/bin/env python2
## -*- coding: utf-8 -*-
##
## main.py
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

import os

try:
    import cPickle as pickle
except ImportError:
    import pickle

from matcher import Matcher
from interface import Interface

case_filename = "cases.pickle"

def main():
    if os.path.exists(case_filename):
        with open(case_filename, "rb") as fp:
            cases = pickle.load(fp)
    else:
        print "Warning: No cases found (looking in '%s')." % case_filename
        cases = []
    matcher = Matcher(cases)
    interface = Interface(matcher)
    interface.cmdloop()

if __name__ == "__main__":
    main()
