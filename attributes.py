import re
from place import Place

class Attribute(object):
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

    @property
    def value(self):
        """Attribute value"""
        return self._value

    @value.setter
    def value(self,value):
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

class attribute_names:
    """Namespace for classes corresponding to actual attribute names"""

    class JourneyCode(Numeric):
        """JourneyCode attribute - standard attribute (not used in matching)"""
        _matching = False

    class HolidayType(Attribute):
        """HolidayType attribute - manual grouping of possible values in distance"""

    class Price(LessIsPerfect, LinearAdjust):
        """Price attribute - simple linear less is perfect matching.
        Adjusted as a result of adaptation of other parameters."""

    class NumberOfPersons(LinearMatch, NumericAdapt):
        """Number of persons. Match linearly, then adapt."""

    class Region(Attribute):
        """Region attribute. Does geographical matching, based on geopy,
        to get (estimated) coordinates of the region, and does similarity
        matching based on this."""

        _scale = 1.0

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            """Convert a location value into a place"""
            if type(value) == type(self):
                self._value = value._value
                return
            self._value = Place(value)

        def similarity(self, other):
            return 1.0-self.value.distance(other.value)/self._scale

    class Transportation(TableMatch):
        """Transportation attribute. Does manual table based matching"""
        _match_table = {'plane': {'plane': 1.0, 'train': 0.0, 'car': 0.0,}}

    class Duration(LinearMatch, NumericAdapt):
        """Duration of holiday. Match linearly, then adapt."""

    class Season(Attribute):
        pass

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
                                    ("|".join(map(str,_numbers_rev.keys()+_numbers_rev.values()))+")"))
        _scale = 4.0

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            """Convert a value of type 'TwoStars' into an integer"""
            if type(value) == type(self):
                self._value = value._value
                return

            m = _numbers_match.match(str(value))
            if m is None:
                raise RuntimeError("Unrecognised value for %s: '%s'" % (self.name, value))
            value = m.group("number")
            try:
                int_val = int(value)
                self._value = int_val
            except ValueError:
                self._value = self._numbers_rev[value]

        def __str__(self):
            return "%s stars" % self._numbers[self.value]

    class Hotel(ExactMatch):
        """Hotel attribute. Only matches exact name of hotel."""
