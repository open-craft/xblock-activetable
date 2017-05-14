# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from selenium.webdriver.support.ui import WebDriverWait
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable_test import StudioEditableBaseTest

loader = ResourceLoader(__name__)  # pylint: disable=invalid-name


class TestActiveTable(StudioEditableBaseTest):
    """Test the Student View of ActiveTableXBlock."""

    def load_scenario(self, path):
        self.set_scenario_xml(loader.load_unicode(path))
        self.element = self.go_to_view("student_view")

    def enter_answers(self, answers):
        for cell_id, value in answers.iteritems():
            text_input = self.element.find_element_by_css_selector('#{id} input'.format(id=cell_id))
            text_input.clear()
            text_input.send_keys(value)

    def get_current_answers(self):
        return {
            cell.get_attribute('id'): cell.get_attribute('value')
            for cell in self.element.find_elements_by_css_selector('td.active')
        }

    def check(self, expected_message, expected_status_class):
        """Click the check button and verify the status message and icon."""
        status_message_div = self.element.find_element_by_class_name('status-message')
        old_message = status_message_div.text
        check_button = self.element.find_element_by_css_selector('.action button.check')
        check_button.click()
        wait = WebDriverWait(status_message_div, self.timeout)
        wait.until(
            lambda e: e.text != old_message,
            'Timeout while waiting for status message to change.'
        )
        self.assertEqual(status_message_div.text, expected_message)
        self.wait_until_exists('.status.' + expected_status_class)

    def verify_cell_classes(self, answers_correct):
        for cell in self.element.find_elements_by_css_selector('td.active'):
            cell_id = cell.get_attribute('id')
            text_input = cell.find_element_by_tag_name('input')
            cell_classes = cell.get_attribute('class')
            if answers_correct[cell_id]:
                self.assertIn('right-answer', cell_classes)
            else:
                self.assertIn('wrong-answer', cell_classes)

    def answer_and_check(self, answers, answers_correct, expected_message):
        self.enter_answers(answers)
        expected_status_class = 'correct' if all(answers_correct.values()) else 'incorrect'
        self.check(expected_message, expected_status_class)
        self.verify_cell_classes(answers_correct)

    def test_basic_answering(self):

        def cell_dict(*values):
            return dict(zip(['cell_1_1', 'cell_2_1', 'cell_3_1'], values))

        self.load_scenario('xml/basic.xml')
        self.answer_and_check(
            answers=cell_dict('', '', ''),
            answers_correct=cell_dict(False, False, False),
            expected_message='You have 0 out of 3 cells correct.',
        )
        self.answer_and_check(
            answers=cell_dict('1789', '1984', '1994'),
            answers_correct=cell_dict(True, False, True),
            expected_message='You have 2 out of 3 cells correct.',
        )
        self.answer_and_check(
            answers=cell_dict('1789', '1883', '1994'),
            answers_correct=cell_dict(True, True, True),
            expected_message='Great job!',
        )

    def test_save_and_reload(self):
        answers = dict(cell_1_1='1', cell_2_1='2', cell_3_1='3')
        self.load_scenario('xml/max_attempts.xml')
        self.enter_answers(answers)
        self.element.find_element_by_css_selector('.action button.save').click()
        vertical = self.load_root_xblock()
        activetable_block = vertical.runtime.get_block(vertical.children[0])
        self.assertEqual(activetable_block.answers, answers)
        # I tried to implement this as reloading the page and testing whether the old values are
        # loaded again.  I can't make that work (while it works perfectly fine when doing it
        # manually).
