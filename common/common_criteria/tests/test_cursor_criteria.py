from datetime import (
    date,
    datetime,
)
from unittest.mock import patch

from common.common_criteria.cursor_criteria import CursorCriteria
from common.common_testcase_helpers.testcase_helpers import SampleModel
from django.db.models import Q
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
        self.assertEqual(len(ordering_data), 3)

        # id__lt -> DESC
        self.assertEqual(ordering_data[0].expression.name, 'id')
        self.assertEqual(ordering_data[0].descending, True)
        self.assertEqual(ordering_data[0].nulls_last, True)

        # created__lte -> DESC
        self.assertEqual(ordering_data[1].expression.name, 'created')
        self.assertEqual(ordering_data[1].descending, True)
        self.assertEqual(ordering_data[1].nulls_last, True)

        # name__gt -> ASC
        self.assertEqual(ordering_data[2].expression.name, 'name')
        self.assertEqual(ordering_data[2].descending, False)
        self.assertEqual(ordering_data[2].nulls_last, True)

    def test_get_filter_q_builds_lexicographic_or_condition(self):
        class SampleCriteria(CursorCriteria):
            cursor_keys = ['consumed_at__lte', 'id__lt']

        decoded = {
            'consumed_at__lte': '2025-01-01T00:00:00+09:00',
            'id__lt': 10,
        }

        q = SampleCriteria.get_filter_q(decoded)
        expected = Q(consumed_at__lt='2025-01-01T00:00:00+09:00') | (
            Q(consumed_at='2025-01-01T00:00:00+09:00') & Q(id__lt=10)
        )
        self.assertEqual(q, expected)

    def test_get_filter_q_three_keys(self):
        class SampleCriteria(CursorCriteria):
            cursor_keys = [
                'consumed_at__lte',
                'moved_to_consumed_section_at__lte',
                'id__lt',
            ]

        decoded = {
            'consumed_at__lte': '2025-01-01T00:00:00+09:00',
            'moved_to_consumed_section_at__lte': '2025-01-01T00:00:01+09:00',
            'id__lt': 10,
        }

        q = SampleCriteria.get_filter_q(decoded)
        expected = (
            Q(consumed_at__lt='2025-01-01T00:00:00+09:00')
            | (
                Q(consumed_at='2025-01-01T00:00:00+09:00')
                & Q(moved_to_consumed_section_at__lt='2025-01-01T00:00:01+09:00')
            )
            | (
                Q(consumed_at='2025-01-01T00:00:00+09:00')
                & Q(moved_to_consumed_section_at='2025-01-01T00:00:01+09:00')
                & Q(id__lt=10)
            )
        )
        self.assertEqual(q, expected)
