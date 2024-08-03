from datetime import (
    date,
    datetime,
    timedelta,
    timezone,
)
from unittest.mock import patch

from common.common_utils.string_utils import (
    format_iso8601,
    format_utc,
    generate_random_string_digits,
    get_filtered_by_startswith_text_and_convert_to_standards,
    string_to_list,
)
from django.test import TestCase


@patch("common.common_utils.string_utils.random.choice")
class TestStringUtils(TestCase):
    def test_generate_random_string_digits_default_length(self, mock_choice):
        # Given: Mocking random
        mock_choice.return_value = "1"

        # When:
        result = generate_random_string_digits()

        # Then:
        self.assertEqual(len(result), 4)
        self.assertEqual(result, "1111")

    def test_generate_random_string_digits_custom_length(self, mock_choice):
        # Given: Mocking random
        mock_choice.return_value = "1"
        length = 6

        # When:
        result = generate_random_string_digits(length)

        # Then:
        self.assertEqual(len(result), length)
        self.assertEqual(result, "111111")

    def test_generate_random_string_digits_zero_length(self, mock_choice):
        # Given: Mocking random
        mock_choice.return_value = "1"

        # When:
        result = generate_random_string_digits(0)

        # Then:
        self.assertEqual(result, '')


class TestFilteredConversion(TestCase):
    def test_get_filtered_by_startswith_text_with_is_integer_true(self):
        # Given:
        input_keys = ['home_popup_modal_1', 'home_popup_modal_2', 'home_popup_modal_3', 'home_popup_modal_4', 'k_popup_modal_10']

        # When: is_integer with True
        result = get_filtered_by_startswith_text_and_convert_to_standards('home_popup_modal_', input_keys, is_integer=True)

        # Then:
        self.assertEqual(result, [1, 2, 3, 4])

    def test_get_filtered_by_startswith_text_with_is_integer_false(self):
        # Given:
        input_keys = ['home_popup_modal_1', 'home_popup_modal_2', 'home_popup_modal_3', 'home_popup_modal_4', 'k_popup_modal_10']

        # When: is_integer with False
        result = get_filtered_by_startswith_text_and_convert_to_standards('home_popup_modal_', input_keys, is_integer=False)

        # Then:
        self.assertEqual(result, ['1', '2', '3', '4'])


class FormatISO8601Tests(TestCase):

    def test_format_datetime(self):
        # Given: A datetime object
        dt = datetime(2024, 5, 1, 13, 0, 0, tzinfo=timezone.utc)

        # When: The datetime object is formatted
        result = format_iso8601(dt)

        # Then: The datetime object is formatted correctly
        self.assertEqual(result, "2024-05-01T13:00:00+00:00")

    def test_format_date(self):
        # Given: A date object
        d = date(2024, 5, 1)

        # When: The date object is formatted
        result = format_iso8601(d)

        # Then: The date object is formatted correctly
        self.assertEqual(result, "2024-05-01T00:00:00+09:00")

    def test_format_date_with_date_timezone(self):
        # Given: A date object
        d = date(2024, 5, 1)

        # When: The date object is formatted
        result = format_iso8601(d, date_timezone='+02:00')

        # Then: The date object is formatted correctly
        self.assertEqual(result, "2024-05-01T00:00:00+02:00")

    def test_invalid_type(self):
        # Given: An object of an unsupported type
        d = 'invalid_type'

        # Expected: A TypeError is raised
        with self.assertRaises(TypeError):
            format_iso8601(d)

    def test_datetime_with_timezone_offset(self):
        # Given: A datetime object with a timezone offset
        dt = datetime(2024, 5, 1, 13, 0, 0, tzinfo=timezone(timedelta(hours=2)))

        # When: The datetime object is formatted
        result = format_iso8601(dt)

        # Then: The datetime object is formatted correctly
        self.assertEqual(result, "2024-05-01T13:00:00+02:00")

    def test_datetime_without_timezone_offset(self):
        # Given: A datetime object with a timezone offset
        dt = datetime(2024, 5, 1, 13, 0, 0)

        # When: The datetime object is formatted
        result = format_iso8601(dt)

        # Then: The datetime object is formatted correctly
        self.assertEqual(result, "2024-05-01T13:00:00+09:00")

    def test_datetime_with_microseconds(self):
        # Given: A datetime object with microseconds
        dt = datetime(2024, 5, 1, 13, 0, 0, 500000, tzinfo=timezone.utc)

        # When: The datetime object is formatted
        result = format_iso8601(dt)

        # Then: The datetime object is formatted correctly
        self.assertEqual(result, "2024-05-01T13:00:00+00:00")


class FormatUTCTests(TestCase):
    def test_naive_datetime(self):
        # Given: A naive datetime object
        naive_dt = datetime(2023, 5, 25, 12, 0)

        # Expected: The datetime object is formatted correctly
        self.assertEqual(format_utc(naive_dt), '2023-05-25T12:00:00Z')

    def test_aware_datetime(self):
        # Given: An aware datetime object
        aware_dt = datetime(2023, 5, 25, 12, 0, tzinfo=timezone(timedelta(hours=-4)))

        # Expected: The datetime object is formatted correctly
        self.assertEqual(format_utc(aware_dt), '2023-05-25T16:00:00Z')

    def test_date(self):
        # Given: A date object
        simple_date = date(2023, 5, 25)

        # Expected: The date object is formatted correctly
        self.assertEqual(format_utc(simple_date), '2023-05-24T15:00:00Z')

    def test_adjust_hours(self):
        # Given: A date object
        simple_date = date(2023, 5, 25)

        # Expected: The date object is formatted correctly
        self.assertEqual(format_utc(simple_date, adjust_hours=-5), '2023-05-25T05:00:00Z')

    def test_unsupported_type(self):
        # Given: An object of an unsupported type
        # Expected: A TypeError is raised
        with self.assertRaises(TypeError):
            format_utc('2023-05-25')


class StringToListTest(TestCase):
    def test_with_default_separator(self):
        # Given: A string with numbers separated by commas and spaces
        input_string = '1, 2, 3, 4, 5'

        # When: string_to_list is called with the default separator
        result = string_to_list(input_string)

        # Then: The output should be a list of numbers as strings without spaces
        self.assertEqual(result, ['1', '2', '3', '4', '5'])

    def test_with_custom_separator(self):
        # Given: A string with numbers separated by semicolons and spaces
        input_string = '1; 2; 3; 4; 5'

        # When: string_to_list is called with a semicolon as the separator
        result = string_to_list(input_string, separator=';')

        # Then: The output should be a list of numbers as strings without spaces
        self.assertEqual(result, ['1', '2', '3', '4', '5'])

    def test_with_no_spaces(self):
        # Given: A string with numbers separated by commas without spaces
        input_string = '1,2,3,4,5'

        # When: string_to_list is called
        result = string_to_list(input_string)

        # Then: The output should be a list of numbers as strings
        self.assertEqual(result, ['1', '2', '3', '4', '5'])

    def test_with_empty_string(self):
        # Given: An empty string
        input_string = ''

        # When: string_to_list is called
        result = string_to_list(input_string)

        # Then: The output should be an empty list
        self.assertEqual(result, [])

    def test_with_spaces_only(self):
        # Given: A string of only spaces and commas
        input_string = ' , , , , '

        # When: string_to_list is called
        result = string_to_list(input_string)

        # Then: The output should be a list with empty strings for each space segment
        self.assertEqual(result, [])

    def test_with_non_standard_characters(self):
        # Given: A string with numbers separated by hash signs
        input_string = "1#2#3#4#5"

        # When: string_to_list is called with a hash sign as the separator
        result = string_to_list(input_string, separator='#')

        # Then: The output should be a list of numbers as strings
        self.assertEqual(result, ['1', '2', '3', '4', '5'])

    def test_with_mixed_separators(self):
        # Given: A string with mixed separators
        input_string = "1,2;3.4/5"

        # When: string_to_list is called with a comma as the separator
        result = string_to_list(input_string, separator=',')

        # Then: The output should treat non-comma separators as part of the string values
        self.assertEqual(result, ['1', '2;3.4/5'])

    def test_strip_elements(self):
        # Given: A string with numbers surrounded by spaces and separated by commas
        input_string = " a , b , c , d "

        # When: string_to_list is called
        result = string_to_list(input_string)

        # Then: The output should be a list of numbers as strings, stripped of surrounding spaces
        self.assertEqual(result, ['a', 'b', 'c', 'd'])
