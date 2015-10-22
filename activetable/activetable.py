# -*- coding: utf-8 -*-
"""An XBlock with a tabular problem type that requires students to fill in some cells."""
from __future__ import absolute_import, division, unicode_literals

import textwrap

from xblock.core import XBlock
from xblock.fields import Dict, Float, Integer, Scope, String
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .cells import NumericCell
from .parsers import ParseError, parse_table, parse_number_list

loader = ResourceLoader(__name__)  # pylint: disable=invalid-name


class ActiveTableXBlock(StudioEditableXBlockMixin, XBlock):
    """An XBlock with a tabular problem type that requires students to fill in some cells."""

    display_name = String(
        display_name='Display Name',
        help='The title Studio uses for the component.',
        scope=Scope.settings,
        default='ActiveTable problem'
    )
    table_definition = String(
        display_name='Table definition',
        help='The definition of the table in Python-like syntax.',
        scope=Scope.content,
        multiline_editor=True,
        resettable_editor=False,
        default=textwrap.dedent("""\
        [
            ['Column header 1', 'Column header 2'],
            ['Enter "answer" here:', String(answer='answer')],
            [42, Numeric(answer=42, tolerance=0.0)],
        ]
        """)
    )
    help_text = String(
        display_name='Help text',
        help='The text that gets displayed when clicking the "+help" button.  If you remove the '
        'help text, the help feature is disabled.',
        scope=Scope.content,
        multiline_editor=True,
        resettable_editor=False,
        default='Fill in the cells highlighted in yellow with the correct answers.  '
        'When you are done, you can check your answers using the button below the table.',
    )
    column_widths = String(
        display_name='Column widths',
        help='Set the width of the columns in pixels.  The value should be a Python-like list of '
        'numerical values.  The total width of the table should not be more than 800. No value '
        'will result in equal-width columns with a total width of 800 pixels.',
        scope=Scope.content,
    )
    row_heights = String(
        display_name='Row heights',
        help='Set the heights of the rows in pixels.  The value should be a Python-like list of '
        'numerical values. Rows may grow higher than the specified value if the text in some cells '
        'in the row is long enough to get wrapped in more than one line.',
        scope=Scope.content,
    )
    default_tolerance = Float(
        display_name='Default tolerance',
        help='The tolerance in pecent that is used for numerical response cells you did not '
        'specify an explicit tolerance for.',
        scope=Scope.content,
        default=1.0,
    )
    max_score = Float(
        display_name='Maximum score',
        help='The number of points students will be awarded when solving all fields correctly.  '
        'For partially correct attempts, the score will be pro-rated.',
        scope=Scope.settings,
        default=1.0,
    )

    editable_fields = [
        'display_name',
        'table_definition',
        'help_text',
        'column_widths',
        'row_heights',
        'default_tolerance',
        'max_score',
    ]

    # Dictionary mapping cell ids to the student answers.
    answers = Dict(scope=Scope.user_state)
    # Number of correct answers.
    num_correct_answers = Integer(scope=Scope.user_state)
    # The number of points awarded.
    score = Float(scope=Scope.user_state)

    has_score = True

    def __init__(self, *args, **kwargs):
        super(ActiveTableXBlock, self).__init__(*args, **kwargs)
        self.thead = None
        self.tbody = None
        self._column_widths = None
        self._row_heights = None
        self.response_cells = None
        self.parse_fields()
        self.postprocess_table()

    def parse_fields(self):
        """Parse the user-provided fields into more processing-friendly structured data."""
        if self.table_definition:
            self.thead, self.tbody = parse_table(self.table_definition)
        else:
            self.thead = self.tbody = None
            return
        if self.column_widths:
            self._column_widths = parse_number_list(self.column_widths)
        else:
            self._column_widths = [800 / len(self.thead)] * len(self.thead)
        if self.row_heights:
            self._row_heights = parse_number_list(self.row_heights)
        else:
            self._row_heights = [36] * (len(self.tbody) + 1)

    def postprocess_table(self):
        """Augment the parsed table definition with further information.

        The additional information is taken from other content and student state fields.
        """
        self.response_cells = {}
        for row, height in zip(self.tbody, self._row_heights[1:]):
            row['height'] = height
            if row['index'] & 1:
                row['class'] = 'even'
            else:
                row['class'] = 'odd'
            for cell in row['cells']:
                cell.id = 'cell_{}_{}'.format(cell.index, row['index'])
                if not cell.is_static:
                    self.response_cells[cell.id] = cell
                    cell.value = self.answers.get(cell.id)
                    cell.height = height - 2
                    if isinstance(cell, NumericCell) and cell.abs_tolerance is None:
                        cell.set_tolerance(self.default_tolerance)
                    if cell.value is None:
                        cell.classes = 'active unchecked'
                    elif cell.check_response(cell.value):
                        cell.classes = 'active right-answer'
                    else:
                        cell.classes = 'active wrong-answer'

    def student_view(self, context=None):
        """Render the table."""
        context = dict(
            help_text=self.help_text,
            total_width=sum(self._column_widths) if self._column_widths else None,
            column_widths=self._column_widths,
            head_height=self._row_heights[0] if self._row_heights else None,
            thead=self.thead,
            tbody=self.tbody,
        )
        html = loader.render_template('templates/html/activetable.html', context)

        css_context = dict(
            correct_icon=self.runtime.local_resource_url(self, 'public/img/correct-icon.png'),
            incorrect_icon=self.runtime.local_resource_url(self, 'public/img/incorrect-icon.png'),
            unanswered_icon=self.runtime.local_resource_url(self, 'public/img/unanswered-icon.png'),
        )
        css = loader.render_template('templates/css/activetable.css', css_context)

        frag = Fragment(html)
        frag.add_css(css)
        frag.add_javascript(loader.load_unicode('static/js/src/activetable.js'))
        frag.initialize_js('ActiveTableXBlock', dict(
            num_correct_answers=self.num_correct_answers,
            num_total_answers=len(self.answers) if self.answers is not None else None,
            score=self.score,
            max_score=self.max_score,
        ))
        return frag

    @XBlock.json_handler
    def check_answers(self, data, unused_suffix=''):
        """Check the answers given by the student.

        This handler is called when the "Check" button is clicked.
        """
        correct = {
            cell_id: self.response_cells[cell_id].check_response(value)
            for cell_id, value in data.iteritems()
        }
        # Since the previous statement executed without error, the data is well-formed enough to be
        # stored.  We now know it's a dictionary and all the keys are valid cell ids.
        self.answers = data
        self.num_correct_answers = sum(correct.itervalues())
        self.score = self.num_correct_answers * self.max_score / len(correct)
        self.runtime.publish(self, 'grade', dict(value=self.score, max_value=self.max_score))
        return dict(
            correct=correct,
            num_correct_answers=self.num_correct_answers,
            num_total_answers=len(correct),
            score=self.score,
            max_score=self.max_score,
        )

    def validate_field_data(self, validation, data):
        """Validate the data entered by the user.

        This handler is called when the "Save" button is clicked in Studio after editing the
        properties of this XBlock.
        """
        def add_error(msg):
            """Add a validation error."""
            validation.add(ValidationMessage(ValidationMessage.ERROR, msg))
        try:
            parse_table(data.table_definition)
        except ParseError as exc:
            add_error('Problem with table definition: ' + exc.message)
        if data.column_widths:
            try:
                parse_number_list(data.column_widths)
            except ParseError as exc:
                add_error('Problem with column widths: ' + exc.message)
        if data.row_heights:
            try:
                parse_number_list(data.row_heights)
            except ParseError as exc:
                add_error('Problem with row heights: ' + exc.message)
