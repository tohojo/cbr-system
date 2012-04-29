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

__all__ = ['Interface']

import re, inspect, sys, cmd

from console import Console
from case import Case
from table_printer import print_table
from util import key_name
from matcher import AdaptationError
import attribute_names

# Possible attribute names are all classes defined in the attribute_names module
possible_attributes = dict(inspect.getmembers(attribute_names, inspect.isclass))

class Interface(Console):
    _default_config = {"retrieve": 2,
                       "adapt": True,
                       "auto_run": True,
                       "auto_display": True,
                       "verbose_results": False}

    def __init__(self, matcher):
        Console.__init__(self)
        self.config = self._default_config
        self.prompt = ">> "
        self.intro = "Welcome to the CBR system. Type 'help' for a list of commands."
        self.matcher = matcher
        if not self.matcher.cases:
            self.intro += "\nNOTE: Currently no cases loaded (you may want to run parser.py to generate some)!"

        self.query = Case()
        self.result = []
        if not sys.stdin.isatty():
            self.prompt = self.intro = ""
            self.interactive = False
            self.config['auto_run'] = False
        else:
            self.interactive = True


    def gen_help(self, method):
        """Generate a help message by removing extra spaces from doc strings"""
        if isinstance(method, basestring):
            helpstring = getattr(self.__class__, method).__doc__
        else:
            helpstring = method.__doc__
        return re.sub("\n *", "\n", helpstring)

    def do_help(self, arg):
        if arg in ('status', 'query', 'result', 'config', 'exit'):
            Console.do_help(self, arg)
        else:
            print "\n".join(['These are the accepted commands.',
                             'Type help <command> to get help on a specific command.',
                             '',
                             'status    Show summary of system status.',
                             'query     Manipulate and run query.',
                             'result    Show result of a query.',
                             'config    Set config variables.',
                             'exit      Exit application.'])

    def help_help(self):
        print self.gen_help("do_help"),

    def do_status(self, arg):
        """Print current status of system (i.e. how many cases loaded etc)."""
        print "Currently %d cases loaded." % len(self.matcher.cases)
        if self.query:
            print "Current query has %d attributes." % len(self.query)
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

        query [show]                   Show current query.
        query reset                    Reset query to be empty.
        query set <attribute> <value>  Set query attribute <attribute> to <value>.
        query unset <attribute>        Unset query attribute <attribute>.
        query names [attribute]        Show possible attribute names.
        query run                      Run the current query.

        By default, the query is automatically run when changed, and
        the result is automatically displayed when run. This behaviour
        can be changed by setting respectively the 'auto_run' and
        'auto_display' config parameters."""
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
                print "Usage: query set <attribute> <value>."
                return
            arg,key,val = parts
            try:
                self.query[key_name(key, possible_attributes)] = val
                if self.config['auto_run']:
                    self.do_query("run")
            except KeyError:
                print "Invalid attribute name '%s'." % key
                print "Possible attribute names:"
                print "\n".join(["  "+i for i in sorted(possible_attributes.keys())])
            except ValueError, e:
                print str(e)
        elif arg.startswith('unset'):
            parts = arg.split()
            if len(parts) < 2:
                print "Usage: query unset <attribute>."
                return
            arg,key = parts[:2]
            try:
                key = key_name(key, possible_attributes)
                del self.query[key]
                if self.config['auto_run']:
                    self.do_query("run")
            except KeyError:
                print "Attribute '%s' not found." % key
                return
        elif arg.startswith('names'):
            parts = arg.split()
            if len(parts) < 2:
                print "Possible attributes:"
                print_table([dict([(k,v._weight) for (k,v) in possible_attributes.items()]),
                             dict([(k,v._adaptable) for (k,v) in possible_attributes.items()]),
                             dict([(k,v._adjustable) for (k,v) in possible_attributes.items()]),],
                            ["Attribute name", "Weight", "Adaptable", "Adjusted"])
                print "\n".join(("Weight is the weight of the attribute for case similarity.",
                                 "",
                                 "Adaptable specifies whether the attribute can be adapted to",
                                 "the query value.",
                                 "",
                                 "Adjustable specifies whether the attribute is adjusted based",
                                 "on the adaptable ones.",
                                 "",
                                 "Run 'query names <attribute>' for help on an attribute."))

            else:
                try:
                    key = key_name(parts[1], possible_attributes)
                    attr = possible_attributes[key]
                    print "\n".join(("Attribute :  %s" % key,
                                     "Weight    :  %s" % attr._weight,
                                     "Adaptable :  %s" % attr._adaptable,
                                     "Adjusted  :  %s" % attr._adjustable,
                                     ""))
                    print self.gen_help(attr)
                except KeyError:
                    print "Unrecognised attribute name: %s" % parts[1]
        elif arg.startswith('run'):
            if not self.query:
                print "No query to run."
                return
            result = self.matcher.match(self.query, self.config['retrieve'])
            if result:
                if self.config['adapt']:
                    try:
                        result.insert(0, self.matcher.adapt(self.query, result))
                    except AdaptationError:
                        pass
                self.result = (Case(self.query), result)
                if self.config['auto_display']:
                    self.do_result("")
                elif self.interactive:
                    print "Query run successfully. Use the 'result' command to view the result."
            else:
                print "no result."
        else:
            print "Unrecognised argument. Type 'help query' for help."

    def help_query(self):
        print self.gen_help("do_query")

    def complete_query(self, text, line, begidx, endidx):
        return self.completions(text, line, {'set': sorted(possible_attributes.keys()),
                                                   'names': sorted(possible_attributes.keys()),
                                                   'unset': self.query.keys(),
                                                   'show': [],
                                                   'reset': [],
                                                   'run': []})

    def do_result(self, args):
        """Print the current query result.

        Prints a table with the query result, each column
        corresponding to a result. The query that is printed along
        with the result.

        If the verbose_results config parameter is set (default: off),
        the similarities for each attribute is shown after the value
        in the form (normalised/weighed).

        If adaptation is turned on (which is the default; turn it off
        with 'config set adapt 0'), an adapted version of the best
        result is shown along with the results if adaptation is
        possible. Adaptation is possible if any of the parameters of
        the query are adaptable, and the query value differs from the
        value of the best result.

        No adaptation is done if the adapted result is worse (i.e. has
        a lower similarity) than the best query match. This can happen
        if the adjusted attribute is part of the query.

        Note that the query shown in the result can differ from the
        current one, if the query has been altered and not rerun (by
        default, the query is re-run whenever it is altered, but this
        can be changed with the 'auto_run' parameter."""
        if not self.result:
            print "No result."
            return
        query,result = self.result
        header = ["Attribute", "Query"]
        results = [query]
        add = 1
        for i,(sim,res) in enumerate(result):
            if sim == 'adapted':
                header.append("Adapted result (sim. %.3f)" % query.similarity(res))
                add = 0
            else:
                header.append("Result %d (sim. %.3f)" % (i+add, sim))
            if self.config['verbose_results']:
                r = {}
                for k,v in res.items():
                    if k in query:
                        s = query[k].similarity(v)
                        w = query[k].weight
                    else:
                        s = 1.0
                        w = 1.0
                    r[k] = "%s (%.2f/%.2f)" % (v, s/w, s)
                results.append(r)
            else:
                results.append(res)
        print_table(results,header)

    def help_result(self):
        print self.gen_help("do_result")

    def do_config(self, args):
        """View or set configuration variables.

        config [show]              Show current config.
        config set <key> <value>   Set <key> to <value>.

        Configuration keys:
        adapt:                     Whether or not to adapt the best case if not a perfect match.
        auto_display:              Automatically display results after running query.
        auto_run:                  Automatically run query when it changes.
        retrieve:                  How many cases to retrieve when running queries.
        verbose_results:           Show similarities (normalised/weighed) for each attribute."""
        if args in ('', 'show'):
            print "Current config:"
            print_table([self.config], ['Key', 'Value'])
        elif args.startswith('set'):
            parts = args.split(None, 2)
            if len(parts) < 3:
                print "Usage: config set <key> <value>."
                return
            key,value = parts[1:3]
            if not key in self.config:
                print "Unrecognised config key: '%s'" % key
            try:
                if type(self.config[key]) in (int, float):
                    self.config[key] = type(self.config[key])(value)
                elif type(self.config[key]) == bool:
                    if value.lower().strip() in ("1", "t", "y", "yes", "true"):
                        self.config[key] = True
                    elif value.lower().strip() in ("0", "f", "n", "no", "false"):
                        self.config[key] = False
                    else:
                        raise ValueError
            except ValueError:
                print "Invalid type for key %s: '%s'" % (key,value)
        else:
            print "Unrecognised argument."
            self.help_config()

    def help_config(self):
        print self.gen_help('do_config')

    def complete_config(self, text, line, begidx, endidx):
        return self.completions(text, line, {'show': [],
                                             'set': self.config.keys()})

    def completions(self, text, line, completions):
        parts = line.split(None)
        current = []
        if len(parts) == 1 or (len(parts) == 2 and not parts[1] in completions.keys()):
            current = completions.keys()
        elif ((len(parts) == 2 and not text) or (len(parts) == 3) and text) and parts[1] in completions:
            current = completions[parts[1]]
        return [i+" " for i in current if i.lower().startswith(text.lower())]

    def completenames(self, text, line, begidx, endidx):
        completions = ['help', 'query', 'status', 'result', 'config', 'exit']
        if text==line:
            return [i+" " for i in completions if i.startswith(text)]
        return Console.completenames(self, text, line, begidx, endidx)

    def default(self, line):
        print "Invalid command. Type 'help' for a list of commands."

    def postloop(self):
        cmd.Cmd.postloop(self)
        if self.interactive:
            print "Exiting..."

if __name__ == "__main__":
    from matcher import Matcher
    interface = Interface(Matcher())
    interface.cmdloop()
