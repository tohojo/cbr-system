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


from place import Place

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
        if line[0] == "defcase":
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
        # Lines are csv items, we are interested in fields 1 and 2
        key,value = line[1:3]
        # The keys we need start with an uppercase letter
        if key[0].isupper():
            key = key.strip(" :")
            value = re.sub(r"([A-Z])", r" \1", value)
            value = value.strip(" .,")
            item[key] = value
    return item

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        filename = "travel_cases.csv"
    else:
        filename = sys.argv[1]

    if filename.endswith(".csv"):
        items = parse_csv(filename)
    else:
        items = parse_cases(filename)
    print "Parsed %d items" % len(items)
    min_price = max_price = int(items[0]['Price'])
    min_people = max_people = int(items[0]['NumberOfPersons'])
    min_duration = max_duration = int(items[0]['Duration'])

    for item in items:
        price = int(item["Price"])
        people = int(item['NumberOfPersons'])
        duration = int(item['Duration'])
        max_price = max([max_price, price])
        min_price = min([min_price, price])
        max_people = max([max_people, people])
        min_people = min([min_people, people])
        max_duration = max([max_duration, duration])
        min_duration = min([min_duration, duration])

    print "Price: %f-%f, %f" % (min_price, max_price, max_price-min_price)
    print "People: %f-%f, %f" % (min_people, max_people, max_people-min_people)
    print "Duration: %f-%f, %f" % (min_duration, max_duration, max_duration-min_duration)
    print "Accommodation:", sorted(list(set([i['Accommodation'] for i in items])))
    print "Transportation:", sorted(list(set([i['Transportation'] for i in items])))
    print "HolidayType:", sorted(list(set([i['HolidayType'] for i in items])))
    regions = list(set([i['Region'] for i in items]))
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
    print "Latitudal distance: %f-%f, %f, %s" % (min_distance, max_distance, max_distance-min_distance, repr(max_regions))
    print "Direct distance: max %f km" % max_direct_distance

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
            pickle.dump(cases, fp, -1)
            print "done."

    import place
    filename = place.location_cache_filename
    if os.path.exists(filename):
        print "Location cache file %s exists. Not storing location cache." % filename
    else:
        print "Storing location cache in %s..." % filename,
        with open(filename, "wb") as fp:
            pickle.dump(place.location_cache, fp, -1)
            print "done."
