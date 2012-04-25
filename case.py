
from attributes import attribute_names

class Case(object):
    _attrs = {}

    def __setattr__(self, name, value):
        """Overridden __setattr__ to turn attributes into attribute
        classes before setting them (and raising an error if an
        appropriate attribute object cannot be found."""

        if name.startswith("_"):
            super(Case, self).__setattr__(name, value)
        if name in self._attrs:
            self._attrs[name] = value
        else:
            if not hasattr(attribute_names, name):
                raise KeyError("Unable to process attribute name: %s" % name)
            self._attrs[name] = getattr(attribute_names, name)(value)

    def __getattr__(self, name):
        if not name in self._attrs:
            raise AttributeError("Attribute not found: %s" % name)
        return self._attrs[name]

