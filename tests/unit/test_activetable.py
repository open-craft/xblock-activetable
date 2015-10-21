# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import unittest

import mock
from xblock.field_data import DictFieldData
from xblock.runtime import Runtime
from xblock.validation import Validation

from activetable.activetable import ActiveTableXBlock

class ActiveTableTest(unittest.TestCase):

    def setUp(self):
        self.runtime_mock = mock.Mock(spec=Runtime)
        self.block = ActiveTableXBlock(self.runtime_mock, DictFieldData({}), mock.Mock())

    def verify_validation(self, data, expect_success):
        validation = Validation('xblock_id')
        self.block.validate_field_data(validation, data)
        self.assertEqual(bool(validation), expect_success)

    def test_validate_field_data(self):
        data = mock.Mock()
        data.table_definition = 'invalid'
        data.column_widths = ''
        data.row_heights = ''
        self.verify_validation(data, False)
        data.table_definition = '[["header"], [6.283]]'
        self.verify_validation(data, True)
        data.column_widths = 'invalid'        
        self.verify_validation(data, False)
        data.column_widths = '[1, 2, 3]'
        self.verify_validation(data, True)
        data.row_heights = 'invalid'        
        self.verify_validation(data, False)
        data.row_heights = '[1, 2, 3]'
        self.verify_validation(data, True)
