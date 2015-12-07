# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import ddt
import unittest

from activetable.cells import Cell, NumericCell, StaticCell, TextCell
from activetable.parsers import ParseError, parse_table, parse_number_list

@ddt.ddt
class ParserTest(unittest.TestCase):

    def test_parse_table(self):
        table_definition = """
        [
            ['Event', 'Year'],
            ['French Revolution', Numeric(answer=1789)],
            ['Volcano exploded in 1883', Text(answer='Krakatoa')],
            [6.283, 123],
        ]
        """
        thead, tbody = parse_table(table_definition)
        expected = eval(table_definition.strip(), dict(Numeric=NumericCell, Text=TextCell))
        expected_body = []
        for i, row in enumerate(expected[1:], 1):
            cells = []
            for j, cell in enumerate(row):
                if not isinstance(cell, Cell):
                    cell = StaticCell(cell)
                cell.index = j
                cells.append(cell)
            expected_body.append(dict(index=i, cells=cells))
        self.assertEqual(thead, expected[0])
        self.assertEqual(tbody, expected_body)

    @ddt.data(
        'syntax error',
        '"wrong type"',
        '["wrong type"]',
        '[["wrong type in header", Numeric(answer=3)]],',
        '[["header", "header"], "wrong type in body"]',
        '[["header", "header"], ["illegal expression", 1 + 1]]',
        '[["header", "header"], ["inconsistent", "row", "length"]]',
        '[["header", "header"], ["wrong function name", Numerical(answer=3)]]',
        '[["header", "header"], ["wrong argument class", Numeric(3)]]',
        '[["header", "header"], ["wrong argument name", Numeric(giraffe=3)]]',
        '[["header", "header"], ["wrong argument value", Numeric(giraffe="3")]]',
    )
    def test_parse_table_errors(self, table_definition):
        with self.assertRaises(ParseError):
            parse_table(table_definition)

    def test_parse_number_list(self):
        self.assertEquals(parse_number_list('[1, 2.3]'), [1, 2.3])
        for string in [']', '123', '["123"]', '[1j]', 'malformed']:
            with self.assertRaises(ParseError):
                parse_number_list(string)
