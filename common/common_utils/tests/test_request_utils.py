from unittest.mock import Mock

from common.common_utils.request_utils import get_request_ip
from django.test import TestCase


class TestGetRequestIP(TestCase):
    def test_with_x_forwarded_for(self):
        # Given:
        request = Mock()
        request.META = {'HTTP_X_FORWARDED_FOR': '1.2.3.4'}

        # When:
        result = get_request_ip(request)

        # Then:
        self.assertEqual(result, '1.2.3.4')

    def test_without_x_forwarded_for(self):
        # Given:
        request = Mock()
        request.META = {'REMOTE_ADDR': '9.10.11.12'}

        # When:
        result = get_request_ip(request)

        # Then:
        self.assertEqual(result, '9.10.11.12')
