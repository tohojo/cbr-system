## -*- coding: utf-8 -*-
##
## attributes.py
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

from abc import ABCMeta, abstractmethod, abstractproperty

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


    def scale(self, value, input_vals=None):
        """Scale for normalising similarity values.

        Supports specifying a _scale attribute or a _range attribute,
        from which the scale is then calculated.

        If a range is specified, it is extended if the scaled
        input_values are supplied and are outside the range."""
        if hasattr(self, '_range'):
            if input_vals:
                min_val = min([self._range[0]] + input_vals)
                max_val = max([self._range[1]] + input_vals)
                return value/(max_val-min_val)
            else:
                return value/(range[1]-range[0])
        if hasattr(self, '_scale'):
            return value/self._scale
        return value

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
        return str(self.value)


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
                raise ValueError("Unrecognised value for %s: '%s'." % (self.name, value))


class LinearMatch(Numeric):
    """Matches linearly on a numeric attribute value."""

    _scale = 1.0

    def similarity(self, other):
        """Linear similarity metric - absolute value of numeric
        difference, scaled by self.scale."""
        return 1.0-self.scale(abs(self.value-other.value), [self.value, other.value])

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
            raise ValueError("Unrecognised value for %s: '%s'." % (self.name, value))
        self._value = value

