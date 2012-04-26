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

import re, inspect

from console import Console
from case import Case
from table_printer import print_table
import attribute_names

# Possible attribute names are all classes defined in the attribute_names module
possible_attributes = dict(inspect.getmembers(attribute_names, inspect.isclass))

class Interface(Console):

    def __init__(self, cases=[]):
        Console.__init__(self)
        self.prompt = ">> "
        self.intro = "Welcome to the CBR system. Type 'help' for a list of commands."
        self.cases = cases
        if not cases:
            self.intro += "\nNOTE: Currently no cases loaded (you may want to run parser.py to generate some)!"

        self.query = Case()
        self.result = []

    def gen_help(self, method):
        """Generate a help message by removing extra spaces from doc strings"""
        if isinstance(basestring, method):
            helpstring = getattr(self.__class__, method).__doc__
        else:
            helpstring = method.__doc__
        return re.sub("\n *", "\n", helpstring)

    def do_help(self, arg):
        if arg in ('status', 'query', 'result'):
            Console.do_help(self, arg)
        else:
            print "\n".join(['These are the accepted commands.',
                             'Type help <command> to get help on a specific command.',
                             '',
                             'status    Show summary of system status.',
                             'query     Manipulate and run query.',
                             'result    Show result of a query.',
                             'config    Set config variables.'])

    def help_help(self):
        print self.gen_help("do_help"),

    def do_status(self, arg):
        """Print current status of system (i.e. how many cases loaded etc)."""
        print "Currently %d cases loaded." % len(self.cases)
        if self.query:
            print "Current query has %d properties." % len(self.query)
        else:
            print "No current query."
        if self.result:
            print "Result exists."
        else:
            print "No result exists."

    def help_status(self):
        print self.gen_help("do_status")

    def do_query(self, arg):
        """Manipulate the query.

        query [show]             Show current query.
        query reset              Reset query to be empty.
        query set <key> <value>  Set query attribute <key> to <value>.
        query unset <key>        Unset query attribute <key>.
        query keys [key]         Help on possible keys.
        query run                Run the current query."""
        if arg in ('', 'show'):
            if self.query:
                print_table([self.query], ["Attribute", "Value"])
            else:
                print "No current query."
        elif arg == "reset":
            self.query = Case()
        elif arg.startswith('set'):
            parts = arg.split(None, 2)
            if len(parts) < 3:
                print "Usage: query set <key> <value>."
                return
            arg,key,val = parts
            try:
                self.query[key] = val
            except KeyError:
                print "Invalid attribute name '%s'." % key
                print "Possible attribute keys:"
                print "\n".join(["  "+i for i in sorted(possible_attributes.keys())])
            except ValueError, e:
                print str(e)
        elif arg.startswith('unset'):
            parts = arg.split()
            if len(parts) < 2:
                print "Usage: query unset <key>."
                return
            arg,key = parts[:2]
            if not key in self.query:
                print "Attribute '%s' not found." % key
                return
            del self.query[key]
        elif arg.startswith('keys'):
            parts = arg.split()
            if len(parts) < 2:
                print "Possible attribute keys:"
                print "\n".join(["  "+i for i in sorted(possible_attributes.keys())])
                print "Run query keys <key> for help on a key."
            else:
                key = parts[1]
                if not key in possible_attributes:
                    print "Unrecognised attribute key: %s" % key
                else:
                    print self.gen_help(possible_attributes[key])
        else:
            print "Unrecognised argument. Type 'help query' for help."

    def help_query(self):
        print self.gen_help("do_query")

    def complete_query(self, text, line, begidx, endidx):
        if re.match(r"\s*query\s+(set|keys)", line):
            args = sorted(possible_attributes.keys())
        elif re.match(r"\s*query\s+unset", line):
            args = self.query.keys()
        elif re.match(r"\s*query\s+([^\s]+)?$", line):
            args = ['show','reset','set','unset','keys','run']
        else:
            return []
        if not text:
            return args
        else:
            return [i for i in args if i.startswith(text)]


    def default(self, line):
        print "Invalid command. Type 'help' for a list of commands."


if __name__ == "__main__":
    interface = Interface()
    interface.cmdloop()
