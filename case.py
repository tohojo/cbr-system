from attributes import BaseAttribute
import attribute_names

class Case(dict):
    """Class to represent a case.

    This is basically a dictionary that only accepts keys that have an
    attribute class defined in attributes.attribute_names, and
    converts its keys into Attribute classes.

    Apart from the normal dictionary methods, similarity() and adapt()
    are defined, to respectively compare cases and adapt one case to
    another."""

    def __init__(self, values={}, **kwargs):
        """Constructor populates the case with the dictionary values
        and/or the kwargs."""
        for key,value in values.items() + kwargs.items():
            self[key] = value

    def __setitem__(self, name, value):
        """Overridden __setitem__ to turn attributes into attribute
        classes before setting them (and raising an error if an
        appropriate attribute object cannot be found).

        If an Attribute instance is assigned to a key, it is set as
        the key directly. Otherwise, a new Attribute object is always
        created for a value. The fact that attributes are never
        modified makes it safe to share them between classes."""

        if isinstance(value, BaseAttribute):
            super(Case, self).__setitem__(name,value)
        else:
            if not hasattr(attribute_names, name):
                raise KeyError("Unable to process attribute name: %s" % name)
            super(Case, self).__setitem__(name,getattr(attribute_names, name)(value))

    def __repr__(self):
        return "<Case: %s>" % (", ".join(map(repr, self.values())))

    def similarity(self, other):
        """Compute total similarity between cases. Total similarity is
        calculated as the sum of the similarities for individual
        attributes, normalised to the sum of all attribute weights."""

        total_weight = 0.0
        total_similarity = 0.0
        for attr in self.values():
            if attr.matching:
                try:
                    total_similarity += attr.similarity(other[attr.name])
                    total_weight += attr.weight
                except AttributeError:
                    pass # happens if other does not have an attribute of this name
        if total_weight == 0.0:
            return 0.0
        return total_similarity / total_weight

    def adapt(self, other):
        """Adapt this case to fit other case.

        This is done by combining all attribute adaptations and
        applying this final adaptation to all attributes that are set
        to be adjusted by adaptation.

        Returns a final new case."""
        total_adapt = 1.0
        new_case = Case()

        # First pass: Compute adaptation level from all adaptable
        # attributes that exists in both case objects.
        for attr in self.values():
            if attr.adaptable and attr.name in other:
                total_adapt *= attr.adapt_distance(other[attr.name])

        # Second pass: Copy all attributes into the new object; for
        # adaptable attributes, use the values from other, for
        # adjustable attributes, adjust them by the adapt value
        for attr in self.all_attributes:
            if attr.adaptable and attr.name in other:
                new_case[attr.name] = other[attr.name]
            elif attr.adjustable:
                new_case[attr.name] = attr.adjusted(total_adapt)
            else:
                new_case[attr.name] = attr

        return new_case
