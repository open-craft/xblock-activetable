# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import unittest

from activetable.cells import NumericCell, TextCell

class CellTest(unittest.TestCase):

    def test_numeric_cell(self):
        cell = NumericCell(answer=42, tolerance=1.0)
        self.assertTrue(cell.check_response('42'))
        self.assertTrue(cell.check_response('42.4'))
        self.assertTrue(cell.check_response('41.6'))
        self.assertFalse(cell.check_response('41.5'))
        self.assertFalse(cell.check_response('43'))
        self.assertFalse(cell.check_response('Hurz!'))
        cell.set_tolerance(10.0)
        self.assertTrue(cell.check_response('42'))
        self.assertTrue(cell.check_response('46'))
        self.assertFalse(cell.check_response('37'))

    def test_significant_digits(self):
        cell = NumericCell(
            answer=6.238, tolerance=10.0, min_significant_digits=3, max_significant_digits=4
        )
        self.assertTrue(cell.check_response('6.24'))
        self.assertTrue(cell.check_response('6.238'))
        self.assertFalse(cell.check_response('6.2'))
        self.assertFalse(cell.check_response('6.2382'))

    def test_string_cell(self):
        cell = TextCell('OpenCraft')
        self.assertTrue(cell.check_response('OpenCraft'))
        self.assertTrue(cell.check_response(' OpenCraft \t\r\n'))
        self.assertFalse(cell.check_response('giraffe'))
        cell = TextCell('ÖpenCräft')
        self.assertTrue(cell.check_response('ÖpenCräft'))
