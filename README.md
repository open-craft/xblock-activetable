ActiveTable XBlock
==================

![Travis CI](https://travis-ci.org/open-craft/xblock-activetable.svg?branch=master)

This XBlock provides a tabular problem type, where students have to fill in some of the cells of a
table.


Running the tests
-----------------

Install the test prerequisites:

```
python -m venv venv
source venv/bin/activate
pip install -r test-requirements.txt
pip install -r $VIRTUAL_ENV/src/xblock-sdk/requirements/base.txt
pip install -r $VIRTUAL_ENV/src/xblock-sdk/requirements/test.txt
pip install -r $VIRTUAL_ENV/src/xblock/requirements/base.txt
pip install -r $VIRTUAL_ENV/src/xblock/requirements/test.txt
```

Run pycodestyle:

    pycodestyle --max-line-length=100 activetable

Run pylint:

    pylint activetable

Run the unit and integration tests:

    coverage run ./run_tests.py


## Installation

1. Install this module in the python environment for studio and lms.
2. Add `"activetable"` to the Advanced Module List array in Advanced
   Settings in Studio for each course this should be installed in.


The table definition
--------------------

The table definition is entered in a Python-like syntax (actually in a strict subset of Python).  It
must be a list of lists, with all inner lists having the same lengths.  The elements of the inner
lists correspond to the cells of the table.  The first line contains the column headers and can only
contain string literals.  All further lines represent the table body.  Cells can be either string
literals, e.g. `'a string'`, numbers, e.g. `6.23`, or response cell declarations.  There are two
types of response cells:

    Numeric(answer=<correct_answer>, tolerance=<tolerance in percent>,
            min_significant_digits=<number>, max_significant_digits=<number>)

A cell that expects a numeric answer.  The tolerance is optional, and will default to the default
tolerance specified above.  The restrictions for the number of significant digits are optional as
well.  Significant digits are counted started from the first non-zero digit specified by the
student, and include trailing zeros.

    Text(answer='<correct answer>')

A cell that expects a string answer.

An example of a table definition:

    [
        ['Event', 'Year'],
        ['French Revolution', Numeric(answer=1789)],
        ['Krakatoa volcano explosion', Numeric(answer=1883)],
        ["Proof of Fermat's last theorem", Numeric(answer=1994)],
    ]
