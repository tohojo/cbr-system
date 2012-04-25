
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
        return self._value

    def __init__(self, value=None, weight=1.0):
        self.value = value
        self.weight = weight

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



# Classes for actual attributes (names match the attribute names)
class JourneyCode(Attribute):
    pass

class HolidayType(Attribute):
    pass

class Price(LessIsPerfect):
    pass

class NumberOfPersons(ExactMatch, NumericAdapt):
    pass

class Region(Attribute):
    pass

class Transportation(Attribute):
    pass

class Duration(LinearMatch, NumericAdapt):
    pass

class Season(Attribute):
    pass

class Accomodation(Attribute):
    pass

class Hotel(ExactMatch):
    pass


