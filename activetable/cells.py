# -*- coding: utf-8 -*-
"""Classes representing table cells.

These classes are used mainly as namespaces to dump all data associated with a cell.  There is no
expectation that all attributes are set in __init__() or that attributes are controlled byt the
classes themselves.
"""
from __future__ import absolute_import, division, unicode_literals

import decimal


class Cell(object):
    """Abstract base class for all cells."""

    is_static = False

    def __eq__(self, other):
        """Test for equality based on type and attribute values."""
        return type(self) is type(other) and vars(self) == vars(other)


class StaticCell(Cell):
    """A static cell with a fixed value in the table body."""

    is_static = True

    def __init__(self, value):
        self.value = value


class NumericCell(Cell):
    """A numeric response cell."""

    placeholder = 'numeric response'

    def __init__(self, answer, tolerance=None,
                 min_significant_digits=None, max_significant_digits=None):
        """Set the correct answer and the allowed relative tolerance in percent."""
        self.answer = answer
        self.abs_tolerance = None
        self.set_tolerance(tolerance)
        self.min_significant_digits = min_significant_digits
        self.max_significant_digits = max_significant_digits

    def set_tolerance(self, tolerance):
        """Set the tolerance to the specified value, if it is not None."""
        if tolerance is not None:
            self.abs_tolerance = abs(self.answer) * tolerance / 100.0

    def check_response(self, student_response):
        """Return a Boolean value indicating whether the student response is correct."""
        try:
            value = float(student_response)
        except ValueError:
            return False
        if self.min_significant_digits or self.max_significant_digits:
            digits = len(decimal.Decimal(student_response).as_tuple().digits)
            if self.min_significant_digits and digits < self.min_significant_digits:
                return False
            if self.max_significant_digits and digits > self.max_significant_digits:
                return False
        return abs(value - self.answer) <= self.abs_tolerance


class TextCell(Cell):
    """A string response cell."""

    placeholder = 'text response'

    def __init__(self, answer):
        """Set the correct answer."""
        self.answer = answer

    def check_response(self, student_response):
        """Return a Boolean value indicating whether the student response is correct."""
        return student_response.strip() == self.answer.strip()
