## -*- coding: utf-8 -*-
##
## interface.py
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

import re

from console import Console

class Interface(Console):

    def __init__(self, cases=[]):
        Console.__init__(self)
        self.prompt = ">> "
        self.intro = "Welcome to the CBR system. Type 'help' for a list of commands."
        self.cases = cases
        if not cases:
            self.intro += "\nNOTE: Currently no cases loaded (you may want to run parser.py to generate some)!"

    def gen_help(self, method):
        """Generate a help message by removing extra spaces from doc strings"""
        helpstring = getattr(self.__class__, method).__doc__
        return re.sub("\n *", "\n", helpstring)

    def help_help(self):
        print self.gen_help("do_help"),

    def do_status(self, arg):
        """Print current status of system (i.e. how many cases loaded etc)."""
        print "Current %d cases loaded." % len(self.cases)

    def help_status(self):
        print self.gen_help("do_status")

    def default(self, line):
        print "Invalid command. Type 'help' for a list of commands."


if __name__ == "__main__":
    interface = Interface()
    interface.cmdloop()
