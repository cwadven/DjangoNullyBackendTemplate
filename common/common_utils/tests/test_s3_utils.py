import unittest
from unittest.mock import (
    Mock,
    patch,
)

import requests
from botocore.exceptions import NoCredentialsError
from common.common_utils.s3_utils import (
    generate_pre_signed_url_info,
    upload_file_to_presigned_url,
)
from django.conf import settings
from django.test import TestCase


class TestGeneratePresignedURLInfo(TestCase):
    @patch('common.common_utils.s3_utils.boto3.client')
    def test_generate_pre_signed_url_info(self, mock_boto3_client):
        # Given: Set up the test data
        file_name = 'test.txt'
        _type = 'test'
        unique = '123'
        expires_in = 3600

        # Mock the boto3.client and s3_client.generate_presigned_post calls
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_generate_presigned_post_response = {
            'url': 'https://s3-bucket-url.com',
            'fields': {
                'key': 'mock-key',
                'AWSAccessKeyId': 'mock-access-key',
                'Policy': 'mock-policy',
                'Signature': 'mock-signature'
            }
        }
        mock_s3_client.generate_presigned_post.return_value = mock_generate_presigned_post_response

        # When: Call the function
        response = generate_pre_signed_url_info(file_name, _type, unique, expires_in)

        # Then: Assert that s3_client.generate_presigned_post is called with the correct data
        mock_boto3_client.assert_called_once_with(
            's3',
            region_name='ap-northeast-2',
            aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
            config=unittest.mock.ANY  # Ensure that the Config object is created
        )
        mock_s3_client.generate_presigned_post.assert_called_once_with(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=unittest.mock.ANY,  # Ensure the Key is generated with a UUID
            Conditions=[
                ['content-length-range', 0, 10485760]
            ],
            ExpiresIn=expires_in  # Ensure the ExpiresIn parameter is passed correctly
        )

        # Assert the response
        expected_response = mock_generate_presigned_post_response
        self.assertEqual(response, expected_response)

    @patch('common.common_utils.s3_utils.boto3.client', side_effect=NoCredentialsError())
    def test_generate_pre_signed_url_info_with_exception(self, mock_boto3_client):
        # Given: Set up the test data
        file_name = 'test.txt'
        _type = 'test'
        unique = '123'
        expires_in = 3600

        # When: Call the function and expect an exception
        with self.assertRaises(Exception):
            generate_pre_signed_url_info(file_name, _type, unique, expires_in)


class TestUploadFileToPresignedURL(unittest.TestCase):
    @patch('common.common_utils.s3_utils.requests.post')
    def test_upload_file_to_presigned_url(self, mock_requests_post):
        # Given: Set up the test data
        presigned_url = 'https://example.com/upload'
        presigned_data = {'key': 'value'}
        file_data = b'file_content'

        # Mock the requests.post method
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests_post.return_value = mock_response

        # When: Call the function
        result = upload_file_to_presigned_url(presigned_url, presigned_data, file_data)

        # Then: Assert that requests.post is called with the correct data
        mock_requests_post.assert_called_once_with(
            url=presigned_url,
            data=presigned_data,
            files={'file': file_data}
        )

        # Assert the result
        self.assertTrue(result)

    @patch('common.common_utils.s3_utils.requests.post', side_effect=requests.exceptions.RequestException())
    def test_upload_file_to_presigned_url_with_exception(self, mock_requests_post):
        # Given: Set up the test data
        presigned_url = 'https://example.com/upload'
        presigned_data = {'key': 'value'}
        file_data = b'file_content'

        # When: Call the function and expect an exception
        result = upload_file_to_presigned_url(presigned_url, presigned_data, file_data)

        # Then: Assert that the function returns False when an exception occurs
        self.assertFalse(result)
