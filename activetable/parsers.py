# -*- coding: utf-8 -*-
"""Parsers for structured text data entered by the user."""
from __future__ import absolute_import, division, unicode_literals

import ast
import numbers

from .cells import NumericCell, StaticCell, TextCell


class ParseError(Exception):
    """The table definition could not be parsed."""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


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
        raise ParseError('Could not parse table definition.') from exc

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
                    f"invalid node in row {i}, cell {j}: {type(cell_node).__name__}"
                )
            cell.index = j
            cells.append(cell)
        if len(cells) != len(thead):
            raise ParseError(
                f"row {i} has a different number of columns "
                f"than the previous rows ({len(cells)} vs. {len(thead)})"
            )
        tbody.append(dict(index=i, cells=cells))
    return thead, tbody


def _parse_response_cell(cell_node):
    """Parse a single student response cell definition.

    Response cells are written in function call syntax, either Text(...) or Numeric(...).  All
    arguments must be keyword arguments.
    """
    cell_type = _ensure_type(cell_node.func, ast.Name).id

    # Reject forbidden argument types
    if hasattr(cell_node, 'starargs') and hasattr(cell_node, 'kwargs'):  # Python 2
        forbidden_argument_types = (cell_node.args, cell_node.starargs, cell_node.kwargs)
        kwargs_nodes = tuple()
    else:  # Python 3.5 or newer
        # starargs and kwargs are no longer treated as separate argument types for ast.Call.
        # From https://greentreesnakes.readthedocs.io/en/latest/nodes.html#Call:
        # "Instead of starargs, Starred nodes can now appear in args,
        # and kwargs is replaced by keyword nodes in keywords for which arg is None."
        forbidden_argument_types = (cell_node.args, )
        kwargs_nodes = tuple(
            keyword_node for keyword_node in cell_node.keywords if keyword_node.arg is None
        )
    if any(forbidden_argument_types) or any(kwargs_nodes):
        raise ParseError(
            f"All arguments to {cell_type} must be keyword arguments of the form name=value"
        )

    if cell_type == 'Text':
        cell_class = TextCell
        kwargs = {kw.arg: _ensure_type(kw.value, ast.Str).s for kw in cell_node.keywords}
    elif cell_type == 'Numeric':
        cell_class = NumericCell
        kwargs = {kw.arg: _ensure_type(kw.value, ast.Num).n for kw in cell_node.keywords}
    else:
        raise ParseError(f"invalid cell input type: {cell_type}")
    try:
        return cell_class(**kwargs)
    except Exception as exc:
        raise ParseError('Could not parse cell definition.') from exc


def parse_number_list(source):
    """Parse the given string as a Python list of numbers.

    This is used to parse the column_widths and row_heights lists entered by the user.
    """
    try:
        lst = ast.literal_eval(source)
    except (SyntaxError, ValueError) as exc:
        msg = getattr(exc, 'msg', getattr(exc, 'message', 'Could not parse list of numbers.'))
        raise ParseError(msg) from exc
    if not isinstance(lst, list):
        raise ParseError('not a list')
    if not all(isinstance(x, numbers.Real) for x in lst):
        raise ParseError('all entries must be numbers')
    return lst
