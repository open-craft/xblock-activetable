# -*- coding: utf-8 -*-
"""Classes representing table cells.

These classes are used mainly as namespaces to dump all data associated with a cell.  There is no
expectation that all attributes are set in __init__() or that attributes are controlled byt the
classes themselves.
"""
from __future__ import absolute_import, division, unicode_literals


class StaticCell(object):
    """A static cell with a fixed value in the table body."""

    is_static = True

    def __init__(self, value):
        self.value = value


class NumericCell(object):
    """A numeric response cell."""

    is_static = False
    placeholder = 'numeric response'

    def __init__(self, answer, tolerance=None, min_significant_digits=None, max_significant_digits=None):
        """Set the correct answer and the allowed relative tolerance in percent."""
        self.answer = answer
        self.set_tolerance(tolerance)
        self.min_significant_digits = min_significant_digits
        self.max_significant_digits = max_significant_digits

    def set_tolerance(self, tolerance):
        if tolerance is None:
            self.abs_tolerance = None
        else:
            self.abs_tolerance = abs(self.answer) * tolerance / 100.0

    def check_response(self, student_response):
        """Return a Boolean value indicating whether the student response is correct."""
        try:
            r = float(student_response)
        except ValueError:
            return False
        if self.min_significant_digits or self.max_significant_digits:
            d = len(decimal.Decimal(student_response).as_tuple().digits)
            if self.min_significant_digits and d < self.min_significant_digits:
                return False
            if self.max_significant_digits and d > self.max_significant_digits:
                return False
        return abs(r - self.answer) <= self.abs_tolerance


class StringCell(object):
    """A string response cell."""

    is_static = False
    placeholder = 'text response'

    def __init__(self, answer):
        """Set the correct answer."""
        self.answer = answer

    def check_response(self, student_response):
        """Return a Boolean value indicating whether the student response is correct."""
        return student_response == self.answer
