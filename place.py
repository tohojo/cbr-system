## -*- coding: utf-8 -*-
##
## place.py
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

import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

from geopy import geocoders

geocoder = geocoders.Google(domain="maps.google.co.uk")
location_cache_filename = "location_cache.pickle"

location_cache = {}

if os.path.exists(location_cache_filename):
    with open(location_cache_filename, "rb") as fp:
        try:
            location_cache = pickle.load(fp)
        except pickle.UnPicklingError:
                pass


# Table of replacement keys to get the right place results on a google
# search. Source: Wikipedia :)
correction_table = {"fano": "fanø",
                     "czechia": "czech republic",
                     "erz gebirge": "erzgebirge",
                     "turkish aegean sea": "aegean sea",
                     "riviera": "french riviera",
                     "turkish riviera": "istanbul", # close enough
                     "costa blanca": "costa blance, spain",
                     "teneriffe": "tenerife",
                     "salzberger land": "salzburg",
                     "costa brava": "costa brava, spain",
                     "atlantic": "bordeaux", # It's by the Atlantic, in France
                     "algarve": "algarve, portugal",
                     }


class Place(object):


    def __init__(self, name):
        self.name = name
        key = name.lower()
        if key in correction_table:
            key = correction_table[key]
        if not key in location_cache:
            try:
                search_value = list(geocoder.geocode(key, exactly_one = False))
                location_cache[key] = search_value[0]
            except:
                   print "Unable to find anything: %s" % name
                   location_cache[key] = (None,None)
        self.place_name, self.coords = location_cache[key]

    def distance(self, other):
        """Distance between two places.

        Distance is defined as the difference in *latitudes* between
        the destinations. If distance is used, the points furthest
        from each other are Tenerife and Egypt, even though it can be
        argued that those two are quite similar for the purpose of
        selecting a holiday."""
        if self.coords is None or other.coords is None:
            return 0.0
        return abs(self.coords[0]-other.coords[0])

    def __repr__(self):
        return "<Place: %s>" % repr(self.place_name)


