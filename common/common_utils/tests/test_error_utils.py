from common.common_utils.error_utils import generate_pydantic_error_detail
from django.test import TestCase


class TestGeneratePydanticErrorDetail(TestCase):

    def test_generate_pydantic_error_detail(self):
        # Given: Input values for the function
        error_type = 'value_error'
        message = 'must be less than or equal to max_hours_per_week'
        input_key = 'min_hours_per_week'
        input_value = 10

        # When: Calling the generate_pydantic_error_detail function
        result = generate_pydantic_error_detail(error_type, message, input_key, input_value)

        # Then: Validate the output
        self.assertEqual(result['type'].type, error_type)
        self.assertEqual(result['type'].message_template, f', {message}')
        self.assertEqual(result['loc'], (input_key,))
        self.assertEqual(result['input'], input_value)
        self.assertEqual(result['ctx'], {})
