
class Attribute(object):
    """Base Attribute class, providing an attribute with a name and a
    value, defining equality on these, and providing the similarity
    distance (which by default always matches)."""

    _adaptable = False

    def __init__(self, name, value=None, weight=1.0):
        self.name = name
        self.value = value
        self.weight = weight

    def similarity(self, other):
        """Similarity metric between 0 and the selected weight. By
        default attributes with the same name are always equal."""
        #TODO: What happens when self.value==None / how to handle unselected attributes?
        if self.name == other.name:
            return self.weight
        else:
            return 0.0

    @property
    def adaptable(self):
        return self._adaptable

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


class ExactMatchAttribute(Attribute):
    """Exact matching attribute, that provides a full (i.e. weight
    match) on the same value, and zero similarity otherwise."""

    def similarity(self, other):
        if self.name == other.name and self.value == other.value:
            return self.weight
        else:
            return 0.0

class ExactMatchNumericAdaptAttribute(ExactMatchAttribute):
    """Exact match, but allow numeric adaptation based on this
    attribute."""

    _adaptable = True
    def adapt_distance(self, other):
        """Return the adaptation distance, which is a positive or
        negative value in the range [0-1] signifying how large an
        adaptation is required to turn this attribute value into the
        other one.

        Straight-forward numeric fraction of difference in relation to
        the current value."""
        return float(other.value-self.value)/self.value

# Maps attribute names to classes
name_map = {'JourneyCode': Attribute,
            'HolidayType': TypeAttribute,
            'Price': LessIsPerfectAttribute,
            'NumberOfPersons': ExactMatchNumericAdaptAttribute,
            'Region': RegionAttribute,
            'Transportation': TransportationAttribute,
            'Duration': LinearMatchNumericAdaptAttribute,
            'Season': SeasonAttribute,
            'Accomodation': AccomodationAttribute,
            'Hotel': ExactMatchAttribute}
