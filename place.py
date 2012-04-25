# -* coding: utf-8 *-
from geopy import geocoders

geocoder = geocoders.Google(domain="maps.google.co.uk")

class Place(object):
    _location_cache = {}

    # Table of replacement keys to get the right place results on a google search.
    # Source: Wikipedia :)
    _correction_table = {"fano": "fanø",
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

    def __init__(self, name):
        self.name = name
        key = name.lower()
        if not key in self._location_cache:
            try:
                if key in self._correction_table:
                    key = self._correction_table[key]
                search_value = list(geocoder.geocode(key, exactly_one = False))
                self._location_cache[key] = search_value[0]
            except:
                   print "Unable to find anything: %s" % name
                   self._location_cache[key] = (None,None)
        self.place_name, self.coords = self._location_cache[key]

    def distance(self, other):
        return distance.distance(self.coords, other.coords).km

    def __repr__(self):
        return "<Place: %s>" % repr(self.place_name)
