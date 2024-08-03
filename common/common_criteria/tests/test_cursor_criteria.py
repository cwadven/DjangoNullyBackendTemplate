from datetime import (
    date,
    datetime,
)
from unittest.mock import patch

from common.common_criteria.cursor_criteria import CursorCriteria
from common.common_testcase_helpers.testcase_helpers import SampleModel
from django.test import TestCase


class SampleCursorCriteria(CursorCriteria):
    cursor_keys = ['id__lte', 'timestamp__lt', 'name', 'datestamp__gt']


class CursorCriteriaTests(TestCase):
    def test_is_valid_decoded_cursor_valid(self):
        # Given: valid cursor
        cursor = {
            'id__lte': 123,
            'timestamp__lt': '2021-08-01 12:00:00',
            'datestamp__gt': '2021-08-01',
            'name': 'test',
        }
        # Expect: True
        self.assertEqual(
            SampleCursorCriteria.is_valid_decoded_cursor(cursor),
            True,
        )

    def test_is_valid_decoded_cursor_invalid(self):
        # Given: invalid cursor
        cursor = {'id': 123}
        # Expect: False
        self.assertEqual(
            SampleCursorCriteria.is_valid_decoded_cursor(cursor),
            False,
        )

    @patch('common.common_criteria.cursor_criteria.data_to_urlsafe_base64')
    def test_get_encoded_base64_cursor_data(self, mock_data_to_urlsafe_base64):
        # Given: Mock data_to_urlsafe_base64
        mock_data_to_urlsafe_base64.return_value = 'encoded_string'
        # And: Sample data
        data = SampleModel(
            id=1,
            timestamp=datetime(2021, 8, 1, 12, 0),
            name="Project",
            datestamp=date(2021, 8, 1),
        )

        # When: get_encoded_base64_cursor_data
        result = SampleCursorCriteria.get_encoded_base64_cursor_data(data)

        # Then: expected result
        self.assertEqual(result, 'encoded_string')
        # And: data_to_urlsafe_base64 called with expected dict
        expected_dict = {
            'id__lte': 1,
            'timestamp__lt': '2021-08-01T12:00:00+09:00',  # Assumes date formatting in valid_keys handling
            'name': 'Project',
            'datestamp__gt': '2021-08-01T00:00:00+09:00',
        }
        # And: data_to_urlsafe_base64 called with expected dict
        mock_data_to_urlsafe_base64.assert_called_once_with(expected_dict)

    def test_get_encoded_base64_cursor_data_invalid_key(self):
        # Given: Sample data with missing attribute for cursor_keys 'datestamp'
        data = SampleModel(
            id=1,
            name="Project",
            timestamp=datetime(2021, 8, 1),
        )

        # When: get_encoded_base64_cursor_data
        with self.assertRaises(ValueError) as e:
            SampleCursorCriteria.get_encoded_base64_cursor_data(data)

        # Then: expected exception
        self.assertEqual(
            e.exception.args[0],
            'Attribute \'datestamp\' not found in \'SampleModel\'',
        )

    def test_ordering_data_empty(self):
        # Given: SampleEmptyCursorCriteria with no cursor_keys
        class SampleEmptyCursorCriteria(CursorCriteria):
            cursor_keys = []

        # When: get_ordering_data
        ordering_data = SampleEmptyCursorCriteria.get_ordering_data()

        # Then: empty list
        self.assertEqual(ordering_data, [])

    def test_ordering_data_simple_without_underlying(self):
        # Given: SampleEmptyCursorCriteria with cursor_keys
        class SampleEmptyCursorCriteria(CursorCriteria):
            cursor_keys = ['id', 'created']

        # When: get_ordering_data
        ordering_data = SampleEmptyCursorCriteria.get_ordering_data()

        # Then: expected ordering data
        self.assertEqual(ordering_data, [])

    def test_ordering_data_with_operators(self):
        # Given:
        class SampleEmptyCursorCriteria(CursorCriteria):
            cursor_keys = ['id__lt', 'created__lte', 'name__gt']

        # When:
        ordering_data = SampleEmptyCursorCriteria.get_ordering_data()

        # Then:
        self.assertEqual(ordering_data, ['-id', '-created', 'name'])
