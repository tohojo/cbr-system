#!/usr/bin/env python2
## -*- coding: utf-8 -*-
##
## parser.py
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

import csv, re, pprint, os
try:
    import cPickle as pickle
except ImportError:
    import pickle



def parse_csv(filename):
    with open(filename, "rb") as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        return parse_items(reader)

def parse_cases(filename):
    with open(filename, "r") as fp:
        return parse_items([i.split(None, 1) for i in fp])

def parse_items(lines):
    items = []
    current_item = []
    for line in lines:
        if not line:
            continue
        if line[0] == "defcase":
            if current_item:
                items.append(parse_item(current_item))
            current_item = []
        elif [i for i in line if i]:
            current_item.append(line)

    if current_item:
        items.append(parse_item(current_item))

    return items

def parse_item(lines):
    item = {}
    for line in lines:
        # We are interested in the last two fields. For the .csv
        # format they always exist, but for the .cases format they
        # only exist for the interesting fields (which means we can
        # safely skip all the rest).
        try:
            key,value = line[-2:]
        except ValueError:
            continue
        # The keys we need start with an uppercase letter
        if key[0].isupper():
            # Strip formatting characters
            key = key.strip(" :")
            value = value.strip('" .,\n"')
            # Break apart camel-cased values into words.
            value = re.sub(r"(.)([A-Z])", r"\1 \2", value)
            # Normalise spaces
            value = re.sub(r"\s+", r" ", value)
            item[key] = value
    return item

if __name__ == "__main__":
    try:
        import sys
        from place import Place
        if len(sys.argv) < 2:
            print "Usage: %s <filename>." % sys.argv[0]
            sys.exit(1)
        else:
            filename = sys.argv[1]

        if filename.endswith(".csv"):
            items = parse_csv(filename)
        else:
            items = parse_cases(filename)
        print "Parsed %d items" % len(items)

        ranges = {}

        prices = [float(i['Price']) for i in items if 'Price' in i]
        ranges['Price'] = (min(prices), max(prices))
        people = [float(i['NumberOfPersons']) for i in items if 'NumberOfPersons' in i]
        ranges['NumberOfPersons'] = (min(people),max(people))
        durations = [float(i['Duration']) for i in items if 'Duration' in i]
        ranges['Duration'] = (min(durations),max(durations))


        print "Accommodation:", sorted(list(set([i['Accommodation'] for i in items if 'Accommodation' in i])))
        print "Transportation:", sorted(list(set([i['Transportation'] for i in items if 'Transportation' in i])))
        print "HolidayType:", sorted(list(set([i['HolidayType'] for i in items if 'HolidayType' in i])))
        regions = list(set([i['Region'] for i in items if 'Region' in i]))
        regions = [(i, Place(i)) for i in regions]
        pp = pprint.PrettyPrinter(indent=4)
        print "Region:",
        pp.pprint(sorted(regions))
        max_distance = 0.0
        min_distance = 10000.0
        max_regions = []
        max_direct_distance = 0.0
        for region in regions:
            for other_region in regions:
                if not region==other_region:
                    distance = region[1].latitudal_distance(other_region[1])
                    min_distance = min([min_distance,distance])
                    direct_distance = region[1].distance(other_region[1])
                    if direct_distance > max_direct_distance:
                        max_direct_distance = direct_distance
                    if distance > max_distance:
                        max_distance = distance
                        max_regions = [region,other_region]
        ranges['Region'] = (min_distance, max_distance, max_direct_distance)
        for k,v in ranges.items():
            print "%s: %f-%f, %f" % (k, v[0], v[1], v[1]-v[0])

        print "Max direct distance: %f km" % ranges['Region'][2]

        filename = "cases.pickle"
        if os.path.exists(filename):
            print "Case storage file %s exists. Not creating cases." % filename
        else:
            print "Creating and storing Case objects in %s:" % filename
            from case import Case
            cases = []
            for i,item in enumerate(items):
                cases.append(Case(item))
                if (i+1)%100 == 0:
                    print "  %d cases created..." % (i+1)
            print "  Storing cases...",
            with open(filename, "wb") as fp:
                pickle.dump((ranges,cases), fp, -1)
                print "done."
    except RuntimeError, e:
        sys.stderr.write("Fatal error occurred: %s\n" % e)
        sys.exit(1)

