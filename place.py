from geopy import geocoders, distance

geocoder = geocoders.Google()

class Place(object):
    _location_cache = {}

    def __init__(self, name):
        self.name = name
        key = name.lower()
        if not key in self._location_cache:
            self._location_cache[key] = geocoder.geocode(key)
        self.place_name, self.coords = self._location_cache[key]

    def distance(self, other):
        return distance.distance(self.coords, other.coords).km

    def __repr__(self):
        return "<Place: %s>" % self.place_name
