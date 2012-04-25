
from attributes import attribute_names

class Case(object):

    def __init__(self):
        self._attrs = {}

    def __setattr__(self, name, value):
        """Overridden __setattr__ to turn attributes into attribute
        classes before setting them (and raising an error if an
        appropriate attribute object cannot be found."""

        if name.startswith("_"):
            super(Case, self).__setattr__(name, value)
        elif name in self._attrs:
            self._attrs[name].value = value
        else:
            if not hasattr(attribute_names, name):
                raise KeyError("Unable to process attribute name: %s" % name)
            self._attrs[name] = getattr(attribute_names, name)(value)

    def __getattr__(self, name):
        if not name in self._attrs:
            raise AttributeError("Attribute not found: %s" % name)
        return self._attrs[name]

    def all_attributes(self):
        return self._attrs.values()

    def similarity(self, other):
        """Compute total similarity between cases. Total similarity is
        calculated as the sum of the similarities for individual
        attributes, normalised to the sum of all attribute weights."""

        total_weight = 0.0
        total_similarity = 0.0
        for attr in self.all_attributes():
            if attr.matching:
                try:
                    total_similarity += attr.similarity(getattr(other, attr.name))
                    total_weight += attr.weight
                except AttributeError:
                    pass # happens if other does not have an attribute of this name
        if total_weight == 0.0:
            return 0.0
        return total_similarity / total_weight
