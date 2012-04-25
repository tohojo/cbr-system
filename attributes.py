
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

    _adapt_adjust = False
    @property
    def adapt_adjust(self):
        """Whether or not this attribute should be adjusted from the
        resulting magnitude of the adaptation of other attributes
        (e.g. adjust price based on adjustment for number of persons)"""
        return self._adapt_adjust

    # Is this attribute used in matching cases to each other?
    _matching = True
    @property
    def matching(self):
        """Is this attribute used in matching cases to each other?"""
        return self._matching

    @matching.setter
    def matching(self,value):
        self._matching = value

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

    @property
    def weight(self):
        """Weight for this attribute"""
        return self._weight

    def __init__(self, value=None, weight=1.0):
        self.value = value
        self._weight = weight

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

class LinearMatch(Attribute):
    """Matches linearly on a numeric attribute value."""

    _scale = 1.0

    def similarity(self, other):
        """Linear similarity metric - absolute value of numeric
        difference, scaled by self._scale."""
        return 1.0-abs(self.value-other.value)/self._scale

class NumericAdapt(Attribute):
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

    class JourneyCode(Attribute):
        """JourneyCode attribute - standard attribute (not used in matching)"""
        _matching = False

    class HolidayType(Attribute):
        """HolidayType attribute - manual grouping of possible values in distance"""

    class Price(LessIsPerfect):
        """Price attribute - simple linear less is perfect matching.
        Adjusted as a result of adaptation of other parameters."""
        _adapt_adjust = True

    class NumberOfPersons(LinearMatch, NumericAdapt):
        """Number of persons. Match linearly, then adapt."""
        _adaptable = True

    class Region(Attribute):
        """Region attribute. Does geographical matching, based on geopy,
        to get (estimated) coordinates of the region, and does similarity
        matching based on this."""

    class Transportation(TableMatch):
        """Transportation attribute. Does manual table based matching"""
        _match_table = {'plane': {'plane': 1.0, 'train': 0.0, 'car': 0.0,}}

    class Duration(LinearMatch, NumericAdapt):
        pass

    class Season(Attribute):
        pass

    class Accomodation(LinearMatch):
        """Accomodation attribute. Does linear matching on number of
        stars. Value is stored numerically internally, but printed
        nicely."""

        _numbers = {1:"One", 2:"Two", 3:"Three", 4:"Four",5:"Five",}
        _numbers_rev = dict([(j.lower(), i) for (i,j) in _numbers.items()])
        _scale = 4.0

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            """Convert a value of type 'TwoStars' into an integer"""
            try:
                self._value = int(value)
            except ValueError:
                value_number = value.lower().replace("stars", "").replace("star", "")
                if not value_number in self._numbers_rev:
                    raise RuntimeError("Unrecognised value for %s: '%s'" % (self.name, value))
                self._value = self._numbers_rev[value_number]

        def __str__(self):
            return "%sStars" % self._numbers[self.value]

    class Hotel(ExactMatch):
        pass


