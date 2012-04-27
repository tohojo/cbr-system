## -*- coding: utf-8 -*-
##
## attribute_names.py
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

import attributes, tree, place

class JourneyCode(attributes.Numeric):
    """JourneyCode attribute (not used in matching).

    Internal code for a given journey.

    Possible values: positive integers."""
    _matching = False

class HolidayType(attributes.TreeMatch):
    """HolidayType attribute.

    Different types of holiday. Similarity is based on a similarity
    tree for related types of holidays.

    Possible values: Active, Bathing, City, Education, Language,
    Recreation, Skiing, Wandering."""

    _match_tree = tree.Tree(["Holiday", 0.0, [
        ['Active', 1.0, []],
        ['Bathing', 1.0, []],
        ['City', 1.0, []],
        ['Education', 1.0, []],
        ['Language', 1.0, []],
        ['Recreation', 1.0, []],
        ['Skiing', 1.0, []],
        ['Wandering', 1.0, []],
        ]])

    def _set_value(self, value):
        attributes.TreeMatch._set_value(self, value.capitalize())

class Price(attributes.LessIsPerfect, attributes.LinearAdjust):
    """Price of holiday.

    Simple linear matching on price distance, with a less is perfect metric.

    When a case is adapted, this value is adjusted corresponding to
    the magnitude of adaptation of other parameters.

    Possible values: Positive integers."""

    # Price range in test cases is from 279-7161
    _scale = 6882.0
    _range = [279.0, 7161.0]

class NumberOfPersons(attributes.LinearMatch, attributes.NumericAdapt):
    """Number of persons for holiday.

    Matching is linear in number of persons. This attribute can be
    adapted to the desired queried value.

    Possible values: Positive integers."""

    # Range in test cases is from 1-12
    _scale = 11.0
    _range = [1.0, 12.0]

class Region(attributes.Attribute):
    """Holiday region.

    Attribute is looked up using Google Maps, and similarity is
    latitudal distance based on this lookup.

    Possible values: Any place name recognisable by Google Maps (the
    lookup result is shown in parentheses when showing the
    attribute)."""

    # Range for test cases is 0.001972-33.307608, or from Sweden to Egypt
    _range = [0.001972, 33.307608]

    def _set_value(self, value):
        """Convert a location value into a place"""
        if type(value) == place.Place:
            self._value = value
        else:
            self._value = place.Place(value)

    def similarity(self, other):
        return 1.0-self.scale(self.value.distance(other.value), [self.value.coords[0], other.value.coords[0]])

    def __str__(self):
        place_name = self.value.place_name

        if len(place_name) > 25:
            place_name = place_name[:10].strip() + "..." + place_name[-10:].strip()
        return "%s (%s)" % (self.value.name, place_name)

class Transportation(attributes.TableMatch):
    """Type of transportation for a given holiday. Matching is
    table-based between the possible values.

    Possible values: Car, Coach, Train, Plane."""
    _match_table = {'Car':   {'Car': 1.0, 'Coach': 0.8, 'Plane': 0.4, 'Train': 0.5,},
                    'Coach': {'Car': 0.8, 'Coach': 1.0, 'Plane': 0.4, 'Train': 0.7,},
                    'Train': {'Car': 0.4, 'Coach': 0.8, 'Plane': 0.4, 'Train': 1.0,},
                    'Plane': {'Car': 0.0, 'Coach': 0.0, 'Plane': 1.0, 'Train': 0.0,},}

    def _set_value(self, value):
        self._value = value.capitalize()

class Duration(attributes.LinearMatch, attributes.NumericAdapt):
    """Duration of holiday.

    The duration of a holiday, in number of days. Similarity is
    measured linearly in difference between durations. This attribute
    can be adapted to the desired value queried.

    Possible values: Positive integers."""

    # Range in test data is from 3-21
    _scale = 18.0
    _range = [3.0, 21.0]

class Season(attributes.Attribute):
    """Holiday season.

    Time holiday takes place. Matching is done by matching holidays
    that are either in an adjacent month, or the same season (winter,
    spring...) half, and others not at all.

    Possible values: Month names (January...December)."""

    # Month names
    _months = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
    # Seasons. Values are indexes in _months
    _seasons = [[11,0,1], # Winter
                [2,3,4],  # Spring
                [5,6,7],  # Summer
                [8,9,10]] # Autumn

    # Similarity for adjacent months / same season
    _fuzz_similarity = 0.5

    def _set_value(self, value):
        value_norm = value.capitalize()
        if not value_norm in self._months:
            raise ValueError("Unrecognised value for %s: '%s'." % (self.name, value))
        self._value = value_norm

    def similarity(self, other):
        """Similarity metric for season. Perfect match if value is
        the same. Otherwise, _fuzz_similarity if it's an adjacent month
        or the same season"""
        if self.value == other.value:
            return 1.0

        idx_self = self._months.index(self.value)
        idx_other = self._months.index(other.value)
        season_self = 0
        season_other = 0
        for i,season in enumerate(self._seasons):
            if idx_self in season:
                season_self = i
            if idx_other in season:
                season_other = i

        # Return the "fuzz similarity" if the two values are in
        # the same season, or adjacent months. Wraparound on
        # months is not a problem in this case, since that occurs
        # within one season (winter)
        if season_self == season_other or abs(idx_self-idx_other) == 1:
            return self._fuzz_similarity

        return 0.0


class Accommodation(attributes.LinearMatch):
    """Type of accommodation for holiday.

    Number of stars of hotel. A holiday flat is considered 0 stars.
    Matching is linear on number of stars.

    Possible values: Numerical value 0-5, or one of 'Holiday flat',
    (One [star]...Five [stars])."""

    # Dictionaries to turn numbers into words and back. Also
    # specifies the valid values for this attribute.
    _numbers = {0:"Holiday flat",1:"One", 2:"Two", 3:"Three", 4:"Four",5:"Five",}
    _numbers_rev = dict([(j.lower(), i) for (i,j) in _numbers.items()])
    # Compile a regular expression to match for numbers at the
    # start of a string, either in numerical or letter form.
    _numbers_match = re.compile("^\s*(?P<number>"+\
                                ("|".join(map(str,_numbers_rev.keys()+_numbers_rev.values()))+")"), re.I)
    _scale = 4.0

    def _set_value(self, value):
        """Convert a value of type 'TwoStars' into an integer"""
        # Special case for "holiday flat" - seen as 0-star
        if value.lower() == "holiday flat":
            self._value = 0
            return

        m = self._numbers_match.match(str(value))
        if m is None:
            raise ValueError("Unrecognised value for %s: '%s'." % (self.name, value))
        value = m.group("number").lower()
        try:
            int_val = int(value)
            self._value = int_val
        except ValueError:
            self._value = self._numbers_rev[value]

    def __str__(self):
        if self.value == 0:
            return "Holiday flat"
        return "%s stars" % self._numbers[self.value]

class Hotel(attributes.ExactMatch):
    """Name of hotel.

    Only matches exact name of hotel.

    Possible values: Any string."""
