# -*- coding: utf-8 -*-
"""Parsers for structured text data entered by the user."""
from __future__ import absolute_import, division, unicode_literals

import ast
import numbers

from .cells import NumericCell, StaticCell, TextCell


class ParseError(Exception):
    """The table definition could not be parsed."""


def _ensure_type(node, expected_type):
    """Internal helper function for parse_table."""
    if isinstance(node, expected_type):
        return node
    raise ParseError('the structure of the table definition is invalid')


def parse_table(table_definition):
    """Parse the table definition given by the user.

    The string table_defintion is parsed as Python source code.  The data is extracted from the
    parse tree without executing it.  The structure is rigidly validated; on error, ParseError is
    thrown.
    """
    try:
        expr = ast.parse(table_definition.strip(), mode='eval')
    except SyntaxError as exc:
        raise ParseError(exc.msg)

    row_iter = iter(_ensure_type(expr.body, ast.List).elts)
    thead = []
    for cell in _ensure_type(next(row_iter), ast.List).elts:
        thead.append(_ensure_type(cell, ast.Str).s)
    tbody = []
    for i, row_node in enumerate(row_iter, 1):
        cells = []
        for j, cell_node in enumerate(_ensure_type(row_node, ast.List).elts):
            if isinstance(cell_node, ast.Str):
                cell = StaticCell(cell_node.s)
            elif isinstance(cell_node, ast.Num):
                cell = StaticCell(cell_node.n)
            elif isinstance(cell_node, ast.Call):
                cell = _parse_response_cell(cell_node)
            else:
                raise ParseError(
                    'invalid node in row {}, cell {}: {}'.format(i, j, type(cell_node).__name__)
                )
            cell.index = j
            cells.append(cell)
        if len(cells) != len(thead):
            raise ParseError(
                'row {} has a different number of columns than the previous rows ({} vs. {})'
                .format(i, len(cells), len(thead))
            )
        tbody.append(dict(index=i, cells=cells))
    return thead, tbody


def _parse_response_cell(cell_node):
    """Parse a single student response cell definition.

    Response cells are written in function call syntax, either Text(...) or Numeric(...).  All
    arguments must be keyword arguments.
    """
    cell_type = _ensure_type(cell_node.func, ast.Name).id
    if any((cell_node.args, cell_node.starargs, cell_node.kwargs)):
        raise ParseError(
            'all arguments to {} must be keyword arguments of the form name=value'.format(cell_type)
        )
    if cell_type == 'Text':
        cell_class = TextCell
        kwargs = {kw.arg: _ensure_type(kw.value, ast.Str).s for kw in cell_node.keywords}
    elif cell_type == 'Numeric':
        cell_class = NumericCell
        kwargs = {kw.arg: _ensure_type(kw.value, ast.Num).n for kw in cell_node.keywords}
    else:
        raise ParseError('invalid cell input type: {}'.format(cell_type))
    try:
        return cell_class(**kwargs)
    except Exception as exc:
        raise ParseError(exc.message)


def parse_number_list(source):
    """Parse the given string as a Python list of numbers.

    This is used to parse the column_widths and row_heights lists entered by the user.
    """
    try:
        lst = ast.literal_eval(source)
    except (SyntaxError, ValueError) as exc:
        msg = getattr(exc, 'msg', getattr(exc, 'message', None))
        raise ParseError(msg)
    if not isinstance(lst, list):
        raise ParseError('not a list')
    if not all(isinstance(x, numbers.Real) for x in lst):
        raise ParseError('all entries must be numbers')
    return lst
