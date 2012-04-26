import re
from abc import ABCMeta, abstractmethod, abstractproperty

from place import Place
from tree import Tree

class BaseAttribute(object):
    __metaclass__ = ABCMeta
    """Base class that Attribute inherits from. Specifies the
    interface that Attribute classes must conform to. Attribute
    contains default implementations of all interface methods."""
    @abstractproperty
    def adaptable(self):
        """Whether or not this attribute can be adapted to form a new
        case."""
        return self._adaptable

    @abstractproperty
    def adjustable(self):
        """Whether or not this attribute should be adjusted from the
        resulting magnitude of the adaptation of other attributes
        (e.g. adjust price based on adjustment for number of persons)"""
        return self._adjustable

    @abstractproperty
    def matching(self):
        """Is this attribute used in matching cases to each other?"""
        return self._matching

    @abstractproperty
    def name(self):
        """Attribute name"""
        return self._name

    @abstractproperty
    def value(self):
        """Attribute name"""
        return self._value

    @abstractproperty
    def weight(self):
        """Weight for this attribute"""
        return self._weight

    @abstractmethod
    def similarity(self, other):
        """Similarity metric between 0 and the selected weight."""
        pass

    @abstractmethod
    def adapt_distance(self, other):
        """Return the adaptation distance, which is a positive or
        negative value in the range [0-1] signifying how large an
        adaptation is required to turn this attribute value into the
        other one."""
        pass

    @abstractmethod
    def adjusted(self, other):
        """Adjust this attribute by a percentage. Return new attribute
        with the adjusted value."""
        pass

class Attribute(BaseAttribute):
    """Base Attribute class, providing an attribute with a name and a
    value, defining equality on these, and providing the similarity
    distance (which by default always matches)."""

    _adaptable = False
    @property
    def adaptable(self):
        """Whether or not this attribute can be adapted to form a new
        case."""
        return self._adaptable

    _adjustable = False
    @property
    def adjustable(self):
        """Whether or not this attribute should be adjusted from the
        resulting magnitude of the adaptation of other attributes
        (e.g. adjust price based on adjustment for number of persons)"""
        return self._adjustable

    _matching = True
    @property
    def matching(self):
        """Is this attribute used in matching cases to each other?"""
        if hasattr(self, "_matching_set"):
            return self._matching_set
        return self._matching

    @matching.setter
    def matching(self,value):
        self._matching_set = value

    @property
    def name(self):
        """Attribute name"""
        return self.__class__.__name__

    @property
    def value(self):
        """Attribute value"""
        return self._value

    @value.setter
    def value(self,value):
        if type(value) == type(self):
            self._value = value._value
        else:
            self._set_value(value)

    def _set_value(self, value):
        "Setter for value - to be overridden in subclasses"
        self._value = value

    _weight = 1.0
    @property
    def weight(self):
        """Weight for this attribute"""
        return self._weight

    def __init__(self, value=None):
        self.value = value

    def similarity(self, other):
        """Similarity metric between 0 and the selected weight. By
        default attributes with the same name are always equal."""
        if self.name == other.name:
            return self.weight
        else:
            return 0.0


    def adapt_distance(self, other):
        """Return the adaptation distance, which is a positive or
        negative value in the range [0-1] signifying how large an
        adaptation is required to turn this attribute value into the
        other one."""
        raise NotImplementedError

    def adjusted(self, value):
        """Adjust this attribute by a percentage. Return new attribute
        with the adjusted value."""
        raise NotImplementedError

    def __eq__(self, other):
        """Equality is on all attributes"""
        return self.name == other.name and self.value == other.value and self.weight == other.weight

    def __repr__(self):
        return "<Attr %s: %s>" % (self.name, self.value)

    def __str__(self):
        """The string representation of an attribute is its value by default"""
        return self.value


class ExactMatch(Attribute):
    """Exact matching attribute, that provides a full (i.e. weight
    match) on the same value, and zero similarity otherwise."""

    def similarity(self, other):
        if self.name == other.name and self.value == other.value:
            return self.weight
        else:
            return 0.0

class Numeric(Attribute):
    """Attribute with numeric values"""

    def _set_value(self,value):
        if type(value) == type(self):
            self._value = value._value
        else:
            try:
                self._value = int(value)
            except ValueError:
                raise RuntimeError("Unrecognised value for %s: %s" % (self.name, value))


class LinearMatch(Numeric):
    """Matches linearly on a numeric attribute value."""

    _scale = 1.0

    def similarity(self, other):
        """Linear similarity metric - absolute value of numeric
        difference, scaled by self._scale."""
        return 1.0-abs(self.value-other.value)/self._scale

class NumericAdapt(Numeric):
    """Exact match, but allow numeric adaptation based on this
    attribute."""

    _adaptable = True
    def adapt_distance(self, other):
        """Return the adaptation distance, i.e. the ratio of the other
        value to the current value. This allows several cumulative
        adaptations to be combined by simple multiplication.

        Straight-forward numeric fraction of difference in relation to
        the current value."""
        return float(other.value)/self.value

class LinearAdjust(Attribute):
    """Linear numeric adjustment of value."""
    _adjustable = True

    def adjusted(self, value):
        return self.__class__(self.value * value)

class LessIsPerfect(LinearMatch):
    """A 'Less is perfect' match, which is a linear match except when
    the other value is less than this one, in which case it is a
    perfect match."""
    #TODO: Which is self, which is other? Consistency! :)

    def similarity(self,other):
        if other.value < self.value:
            return self.weight
        return LinearMatch.similarity(self,other)

class TableMatch(Attribute):
    """Table matching, by comparing values to a predefined table
    (nested dictionaries) to get a similarity measure."""

    _match_table = {}

    def similarity(self, other):
        if not self.value in self._match_table:
            raise RuntimeError("Own value not found in match table: %s" % self.value)
        if not other.value in self._match_table[self.value]:
            raise RuntimeError("Other's value not found in match table: %s" % other.value)
        return self._match_table[self.value][other.value]

class TreeMatch(Attribute):
    """Tree matching, by finding the nearest common ancestor between two values."""

    _match_tree = Tree(["root", 0.0, []])

    def similarity(self, other):
        if self.value == other.value:
            return 1.0

        return self._match_tree.find_common_value([self.value, other.value])

    def _set_value(self, value):
        if self._match_tree.find_path(value) is None:
            raise RuntimeError("Unrecognised value for %s: %s" % (self.name, value))
        self._value = value

class attribute_names:
    """Namespace for classes corresponding to actual attribute names"""

    class JourneyCode(Numeric):
        """JourneyCode attribute - standard attribute (not used in matching)"""
        _matching = False

    class HolidayType(TreeMatch):
        """HolidayType attribute - manual grouping of possible values in distance"""

        _match_tree = Tree(["Holiday", 0.0, [
            ['Active', 1.0, []],
            ['Bathing', 1.0, []],
            ['City', 1.0, []],
            ['Education', 1.0, []],
            ['Language', 1.0, []],
            ['Recreation', 1.0, []],
            ['Skiing', 1.0, []],
            ['Wandering', 1.0, []],
            ]])

    class Price(LessIsPerfect, LinearAdjust):
        """Price attribute - simple linear less is perfect matching.
        Adjusted as a result of adaptation of other parameters."""

        # Price range in test cases is from 279-7161
        _scale = 6882.0

    class NumberOfPersons(LinearMatch, NumericAdapt):
        """Number of persons. Match linearly, then adapt."""

        # Range in test cases is from 1-12
        _scale = 11.0

    class Region(Attribute):
        """Region attribute. Does geographical matching, based on geopy,
        to get (estimated) coordinates of the region, and does similarity
        matching based on this."""

        # Range for test cases is 0.001972-33.307608, or from Sweden to Egypt
        _scale = 33.305636

        def _set_value(self, value):
            """Convert a location value into a place"""
            if type(value) == Place:
                self._value = value
            else:
                self._value = Place(value)

        def similarity(self, other):
            return 1.0-self.value.distance(other.value)/self._scale

        def __str__(self):
            return self.value.name

    class Transportation(TableMatch):
        """Transportation attribute. Does manual table based matching"""
        _match_table = {'Car':   {'Car': 1.0, 'Coach': 0.8, 'Plane': 0.4, 'Train': 0.5,},
                        'Coach': {'Car': 0.8, 'Coach': 1.0, 'Plane': 0.4, 'Train': 0.7,},
                        'Train': {'Car': 0.4, 'Coach': 0.8, 'Plane': 0.4, 'Train': 1.0,},
                        'Plane': {'Car': 0.0, 'Coach': 0.0, 'Plane': 1.0, 'Train': 0.0,},}

        def _set_value(self, value):
            self._value = value.capitalize()

    class Duration(LinearMatch, NumericAdapt):
        """Duration of holiday. Match linearly, then adapt."""

        # Range in test data is from 3-21
        _scale = 18.0

    class Season(Attribute):
        """Season attribute"""

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
                raise RuntimeError("Unrecognised value for %s: %s" % (self.name, value))
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


    class Accommodation(LinearMatch):
        """Accomodation attribute. Does linear matching on number of
        stars. Value is stored numerically internally, but printed
        nicely."""

        # Dictionaries to turn numbers into words and back. Also
        # specifies the valid values for this attribute.
        _numbers = {1:"One", 2:"Two", 3:"Three", 4:"Four",5:"Five",}
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
                raise RuntimeError("Unrecognised value for %s: '%s'" % (self.name, value))
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

    class Hotel(ExactMatch):
        """Hotel attribute. Only matches exact name of hotel."""
