import json
from unittest.mock import (
    Mock,
    patch,
)

from botocore.exceptions import NoCredentialsError
from common.common_utils.aws_sqs_utils import (
    create_sqs_event,
    get_sqs_messages,
)
from django.conf import settings
from django.test import TestCase


class TestCreateSQSEvent(TestCase):
    @patch('common.common_utils.aws_sqs_utils.boto3.client')
    def test_create_sqs_event(self, mock_boto3_client):
        # Given: Set up the test data
        queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'
        event_data = {'key': 'value'}

        # And: Mock the boto3.client and sqs.send_message calls
        mock_sqs_client = Mock()
        mock_boto3_client.return_value = mock_sqs_client
        mock_send_message_response = {'MessageId': '1234567890'}
        mock_sqs_client.send_message.return_value = mock_send_message_response

        # When: Call the function
        response = create_sqs_event(queue_url, event_data)

        # Then: Assert that sqs.send_message is called with the correct data
        mock_boto3_client.assert_called_once_with(
            'sqs',
            region_name='ap-northeast-2',
            aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
        )
        mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl=queue_url,
            MessageBody=json.dumps(event_data),
        )

        # And: Assert the response from the function
        self.assertEqual(response, mock_send_message_response)


class TestGetSQSMessages(TestCase):
    @patch('common.common_utils.aws_sqs_utils.boto3.client')
    def test_get_sqs_messages(self, mock_boto3_client):
        # Given: Set up the test data
        queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'
        message_body = '{"key": "value"}'

        # And: Mock the boto3.client and sqs.receive_message calls
        mock_sqs_client = Mock()
        mock_boto3_client.return_value = mock_sqs_client
        mock_receive_message_response = {
            'Messages': [
                {
                    'Body': message_body,
                    'ReceiptHandle': 'mock-receipt-handle'
                }
            ]
        }
        mock_sqs_client.receive_message.return_value = mock_receive_message_response

        # When: Call the function
        result = get_sqs_messages(queue_url)

        # Then: Assert that sqs.receive_message and sqs.delete_message are called with the correct data
        mock_boto3_client.assert_called_once_with(
            'sqs',
            region_name='ap-northeast-2',
            aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
        )
        mock_sqs_client.receive_message.assert_called_once_with(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1
        )
        mock_sqs_client.delete_message.assert_called_once_with(
            QueueUrl=queue_url,
            ReceiptHandle='mock-receipt-handle'
        )

        # And: Assert the result
        expected_result = {'key': 'value'}
        self.assertEqual(result, expected_result)

    @patch('common.common_utils.aws_sqs_utils.boto3.client', side_effect=NoCredentialsError())
    def test_get_sqs_messages_with_exception(self, mock_boto3_client):
        # Given: Set up the test data
        queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'

        # Expected: Call the function and expect an exception
        with self.assertRaises(Exception):
            get_sqs_messages(queue_url)
