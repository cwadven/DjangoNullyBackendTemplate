import base64
import json

from common.common_utils.encode_utils import data_to_urlsafe_base64
from django.test import TestCase


class TestDataToUrlSafeBase64(TestCase):
    def test_data_to_urlsafe_base64(self):
        # Given: Set up the test data
        test_data = {'name': '홍길동', 'age': 30}
        # And: Set up the expected result
        expected_result = base64.urlsafe_b64encode(
            json.dumps(test_data).encode('utf-8')
        ).decode('utf-8')

        # When: Call the function
        result = data_to_urlsafe_base64(test_data)

        # Then: Assert the result
        self.assertEqual(result, expected_result)
