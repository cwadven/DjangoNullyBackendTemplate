from unittest.mock import (
    Mock,
    patch,
)

from common.common_utils.slack_utils import notify_slack_simple_text
from django.test import TestCase


class TestNotifySlackSimpleText(TestCase):
    @patch('common.common_utils.slack_utils.requests.post')
    def test_notify_slack_simple_text(self, mock_requests_post):
        # Given: Set up the test data and expected values
        channel_url = 'https://slack.com/webhook-url'
        text = 'Hello, Slack!'

        # Mock the requests.post method
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_post.return_value = mock_response

        # When: Call the function
        notify_slack_simple_text(channel_url, text)

        # Then: Assert that the requests.post method is called with the correct data
        mock_requests_post.assert_called_once_with(
            url=channel_url,
            data='{"text": "Hello, Slack!"}',
        )
