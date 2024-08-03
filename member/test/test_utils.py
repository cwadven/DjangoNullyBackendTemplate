import json
from datetime import datetime
from unittest.mock import (
    Mock,
    patch,
)

from django.conf import settings
from django.test import TestCase
from member.exceptions import LoginFailedException, SocialLoginTokenErrorException
from member.utils.social_utils import (
    GoogleSocialLoginModule,
    KakaoSocialLoginModule,
    NaverSocialLoginModule,
    SocialLoginHandler,
    SocialLoginModule,
)


# Given: Create a mock class that inherits from SocialLoginModule
class ExampleSocialLoginModule(SocialLoginModule):
    def request_access_token_path(self):
        return None

    def request_user_info_path(self):
        return None

    def client_id(self):
        return None

    def secret(self):
        return None

    def redirect_uri(self):
        return None

    def username_prefix(self):
        return 'example_'

    def get_user_info_with_access_token(self, access_token: str) -> dict:
        return {}


class TestSocialLoginModule(TestCase):
    @patch('member.utils.social_utils.requests.post')
    def test_get_access_token_by_code_success(self, mock_post):
        # Given: Mock the response from requests.post
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"access_token": "fake_access_token"}'
        mock_post.return_value = mock_response

        # When: Call the method
        access_token = ExampleSocialLoginModule().get_access_token_by_code('code')

        # Then: Assert that the access token is returned correctly
        self.assertEqual(access_token, "fake_access_token")

    @patch('member.utils.social_utils.requests.post')
    def test_get_access_token_by_code_failure(self, mock_post):
        # Given: Mock the response from requests.post
        mock_response = Mock()
        mock_response.status_code = 400  # Simulate a failure status code
        mock_post.return_value = mock_response

        # Expected: Call the method and expect an exception to be raised
        with self.assertRaises(LoginFailedException):
            ExampleSocialLoginModule().get_access_token_by_code('code')

    @patch('member.utils.social_utils.requests.post')
    def test_get_access_token_by_code_missing_token(self, mock_post):
        # Given: Mock the response from requests.post
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"some_other_field": "value"}'  # Missing 'access_token'
        mock_post.return_value = mock_response

        # Expected: Call the method and expect an exception to be raised
        with self.assertRaises(SocialLoginTokenErrorException):
            ExampleSocialLoginModule().get_access_token_by_code('code')


class TestKakaoSocialLoginModule(TestCase):
    def setUp(self):
        self.social_login_module = KakaoSocialLoginModule()

    def test_initialize_kakao_social_login(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module._request_access_token_path, 'https://kauth.kakao.com/oauth/token')
        self.assertEqual(self.social_login_module._request_user_info_path, 'https://kapi.kakao.com/v2/user/me')
        self.assertEqual(self.social_login_module._client_id, settings.KAKAO_API_KEY)
        self.assertEqual(self.social_login_module._secret, settings.KAKAO_SECRET_KEY)
        self.assertEqual(self.social_login_module._redirect_uri, settings.KAKAO_REDIRECT_URL)

    def test_request_access_token_path(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.request_access_token_path, 'https://kauth.kakao.com/oauth/token')

    def test_request_user_info_path(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.request_user_info_path, 'https://kapi.kakao.com/v2/user/me')

    def test_client_id(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.client_id, settings.KAKAO_API_KEY)

    def test_secret(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.secret, settings.KAKAO_SECRET_KEY)

    def test_redirect_uri(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.redirect_uri, settings.KAKAO_REDIRECT_URL)

    def test_username_prefix(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.username_prefix, 'kakao_')

    def test_get_birth_day_valid_data(self):
        # Given:
        data = {
            'kakao_account': {
                'birthyear': '1990',
                'birthday': '0105'
            }
        }
        expected_birth = datetime.strptime('19900105', '%Y%m%d')

        # When:
        birth = self.social_login_module._get_birth_day(data)

        # Then:
        self.assertEqual(birth, expected_birth)

    def test_get_birth_day_missing_keys(self):
        # Given: Missing 'birthyear' and 'birthday' keys
        data = {
            'kakao_account': {}
        }

        # When:
        birth = self.social_login_module._get_birth_day(data)

        # Then:
        self.assertEqual(birth, None)

    def test_get_birth_day_missing_kakao_account(self):
        # Given: Missing 'kakao_account' key
        data = {}

        # When:
        birth = self.social_login_module._get_birth_day(data)

        # Then:
        self.assertEqual(birth, None)

    def test_get_gender_with_kakao_account(self):
        # Given: Input data with 'kakao_account' containing 'gender'
        data = {
            'kakao_account': {
                'gender': 'male'
            }
        }

        # When: Calling the _get_gender method
        gender = self.social_login_module._get_gender(data)

        # Then: The expected gender should be returned
        self.assertEqual(gender, 'male')

    def test_get_gender_missing_kakao_account(self):
        # Given: Input data without 'kakao_account'
        data = {}

        # When: Calling the _get_gender method
        gender = self.social_login_module._get_gender(data)

        # Then: None should be returned as 'kakao_account' is missing
        self.assertEqual(gender, None)

    def test_get_gender_missing_gender_in_kakao_account(self):
        # Given: Input data with 'kakao_account' but missing 'gender'
        data = {
            'kakao_account': {}
        }

        # When: Calling the _get_gender method
        gender = self.social_login_module._get_gender(data)

        # Then: None should be returned as 'gender' is missing
        self.assertEqual(gender, None)

    def test_get_phone_with_kakao_account(self):
        # Given: Input data with 'kakao_account' containing 'phone_number'
        data = {
            'kakao_account': {
                'phone_number': '+82 123-456-7890'
            }
        }

        # When: Calling the _get_phone method
        phone = self.social_login_module._get_phone(data)

        # Then: The expected formatted phone number should be returned
        self.assertEqual(phone, '01234567890')

    def test_get_phone_missing_kakao_account(self):
        # Given: Input data without 'kakao_account'
        data = {}

        # When: Calling the _get_phone method
        phone = self.social_login_module._get_phone(data)

        # Then: None should be returned as 'kakao_account' is missing
        self.assertEqual(phone, None)

    def test_get_phone_missing_phone_number_in_kakao_account(self):
        # Given: Input data with 'kakao_account' but missing 'phone_number'
        data = {
            'kakao_account': {}
        }

        # When: Calling the _get_phone method
        phone = self.social_login_module._get_phone(data)

        # Then: None should be returned as 'phone_number' is missing
        self.assertEqual(phone, None)

    def test_get_email_with_kakao_account(self):
        # Given: Input data with 'kakao_account' containing 'email'
        data = {
            'kakao_account': {
                'email': 'user@example.com'
            }
        }

        # When: Calling the _get_email method
        email = self.social_login_module._get_email(data)

        # Then: The expected email should be returned
        self.assertEqual(email, 'user@example.com')

    def test_get_email_missing_kakao_account(self):
        # Given: Input data without 'kakao_account'
        data = {}

        # When: Calling the _get_email method
        email = self.social_login_module._get_email(data)

        # Then: None should be returned as 'kakao_account' is missing
        self.assertEqual(email, None)

    def test_get_email_missing_email_in_kakao_account(self):
        # Given: Input data with 'kakao_account' but missing 'email'
        data = {
            'kakao_account': {}
        }

        # When: Calling the _get_email method
        email = self.social_login_module._get_email(data)

        # Then: None should be returned as 'email' is missing
        self.assertEqual(email, None)

    def test_get_name_with_kakao_account(self):
        # Given: Input data with 'kakao_account' containing 'profile' with 'nickname'
        data = {
            'kakao_account': {
                'profile': {
                    'nickname': 'JohnDoe'
                }
            }
        }

        # When: Calling the _get_name method
        name = self.social_login_module._get_name(data)

        # Then: The expected nickname should be returned
        self.assertEqual(name, 'JohnDoe')

    def test_get_name_missing_kakao_account(self):
        # Given: Input data without 'kakao_account'
        data = {}

        # When: Calling the _get_name method
        name = self.social_login_module._get_name(data)

        # Then: None should be returned as 'kakao_account' is missing
        self.assertEqual(name, None)

    def test_get_name_missing_nickname_in_kakao_account(self):
        # Given: Input data with 'kakao_account' but missing 'profile' or 'nickname'
        data = {
            'kakao_account': {}
        }

        # When: Calling the _get_name method
        name = self.social_login_module._get_name(data)

        # Then: None should be returned as 'profile' or 'nickname' is missing
        self.assertEqual(name, None)

    @patch('member.utils.social_utils.requests.get')
    def test_get_user_info_with_access_token_successful(self, mock_requests_get):
        # Given: Mock successful response from the requests.get method
        access_token = 'valid_access_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({
            'id': '12345',
            'kakao_account': {
                'birthyear': '1990',
                'birthday': '0105',
                'gender': 'male',
                'phone_number': '+82 123-456-7890',
                'email': 'user@example.com',
                'profile': {
                    'nickname': 'JohnDoe'
                }
            }
        })
        mock_requests_get.return_value = mock_response

        # When: Calling the get_user_info_with_access_token method
        user_info = self.social_login_module.get_user_info_with_access_token(access_token)

        # Then: The expected user information should be returned
        self.assertEqual(user_info['id'], 'kakao_12345')
        self.assertEqual(user_info['gender'], 'male')
        self.assertEqual(user_info['phone'], '01234567890')
        self.assertEqual(user_info['birth'].strftime('%Y-%m-%d'), '1990-01-05')
        self.assertEqual(user_info['email'], 'user@example.com')
        self.assertEqual(user_info['name'], 'JohnDoe')
        self.assertIsNone(user_info['nickname'])

    @patch('member.utils.social_utils.requests.get')
    def test_get_user_info_with_access_token_failed(self, mock_requests_get):
        # Given: Mock failed response from the requests.get method
        access_token = 'invalid_access_token'
        mock_response = Mock()
        mock_response.status_code = 401  # Unauthorized
        mock_requests_get.return_value = mock_response

        # When: Calling the get_user_info_with_access_token method with an invalid token
        # Then: It should raise a LoginFailedException
        with self.assertRaises(LoginFailedException):
            self.social_login_module.get_user_info_with_access_token(access_token)


class TestNaverSocialLoginModule(TestCase):
    def setUp(self):
        self.social_login_module = NaverSocialLoginModule()

    def test_initialize_naver_social_login(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module._request_access_token_path, 'https://nid.naver.com/oauth2.0/token')
        self.assertEqual(self.social_login_module._request_user_info_path, 'https://openapi.naver.com/v1/nid/me')
        self.assertEqual(self.social_login_module._client_id, settings.NAVER_API_KEY)
        self.assertEqual(self.social_login_module._secret, settings.NAVER_SECRET_KEY)
        self.assertEqual(self.social_login_module._redirect_uri, settings.NAVER_REDIRECT_URL)

    def test_request_access_token_path(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.request_access_token_path, 'https://nid.naver.com/oauth2.0/token')

    def test_request_user_info_path(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.request_user_info_path, 'https://openapi.naver.com/v1/nid/me')

    def test_client_id(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.client_id, settings.NAVER_API_KEY)

    def test_secret(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.secret, settings.NAVER_SECRET_KEY)

    def test_redirect_uri(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.redirect_uri, settings.NAVER_REDIRECT_URL)

    def test_username_prefix(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.username_prefix, 'naver_')

    def test_get_birth_day_valid_data(self):
        # Given:
        data = {
            'birthyear': '1990',
            'birthday': '0105'
        }
        expected_birth = datetime.strptime('19900105', '%Y%m%d')

        # When:
        birth = self.social_login_module._get_birth_day(data)

        # Then:
        self.assertEqual(birth, expected_birth)

    def test_get_birth_day_missing_keys(self):
        # Given: Missing 'birthyear' and 'birthday' keys
        data = {}

        # When:
        birth = self.social_login_module._get_birth_day(data)

        # Then:
        self.assertEqual(birth, None)

    def test_get_gender(self):
        # Given: Input data with containing 'gender'
        data = {
            'gender': 'male'
        }

        # When: Calling the _get_gender method
        gender = self.social_login_module._get_gender(data)

        # Then: The expected gender should be returned
        self.assertEqual(gender, 'male')

    def test_get_gender_missing_data(self):
        # Given: Input data without data
        data = {}

        # When: Calling the _get_gender method
        gender = self.social_login_module._get_gender(data)

        # Then: None should be returned as missing
        self.assertEqual(gender, None)

    def test_get_phone_with_phone_number(self):
        # Given: Input data with 'phone_number'
        data_response = {
            'phone_number': '123-456-7890'
        }

        # When: Calling the _get_phone method
        phone = self.social_login_module._get_phone(data_response)

        # Then: The expected formatted phone number should be returned
        self.assertEqual(phone, '1234567890')

    def test_get_phone_missing_phone_number(self):
        # Given: Input data without 'phone_number'
        data_response = {}

        # When: Calling the _get_phone method
        phone = self.social_login_module._get_phone(data_response)

        # Then: None should be returned as 'phone_number' is missing
        self.assertEqual(phone, None)

    def test_get_email_with_kakao_account(self):
        # Given: Input data with containing 'email'
        data = {
            'email': 'user@example.com'
        }

        # When: Calling the _get_email method
        email = self.social_login_module._get_email(data)

        # Then: The expected email should be returned
        self.assertEqual(email, 'user@example.com')

    def test_get_email_missing_kakao_account(self):
        # Given: Input data without
        data = {}

        # When: Calling the _get_email method
        email = self.social_login_module._get_email(data)

        # Then: None should be returned as missing
        self.assertEqual(email, None)

    def test_get_name_with_kakao_account(self):
        # Given: Input data with 'name'
        data = {
            'name': 'JohnDoe'
        }

        # When: Calling the _get_name method
        name = self.social_login_module._get_name(data)

        # Then: The expected nickname should be returned
        self.assertEqual(name, 'JohnDoe')

    def test_get_name_missing_kakao_account(self):
        # Given: Input data without
        data = {}

        # When: Calling the _get_name method
        name = self.social_login_module._get_name(data)

        # Then: None should be returned as missing
        self.assertEqual(name, None)

    @patch('member.utils.social_utils.requests.get')
    def test_get_user_info_with_access_token_successful(self, mock_requests_get):
        # Given: Mock successful response from the requests.get method
        access_token = 'valid_access_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({
            'response': {
                'id': '12345',
                'birthyear': '1990',
                'birthday': '0105',
                'gender': 'male',
                'phone_number': '123-456-7890',
                'email': 'user@example.com',
                'name': 'JohnDoe',
            }
        })
        mock_requests_get.return_value = mock_response

        # When: Calling the get_user_info_with_access_token method
        user_info = self.social_login_module.get_user_info_with_access_token(access_token)

        # Then: The expected user information should be returned
        self.assertEqual(user_info['id'], 'naver_12345')
        self.assertEqual(user_info['gender'], 'male')
        self.assertEqual(user_info['phone'], '1234567890')
        self.assertEqual(user_info['birth'].strftime('%Y-%m-%d'), '1990-01-05')
        self.assertEqual(user_info['email'], 'user@example.com')
        self.assertEqual(user_info['name'], 'JohnDoe')
        self.assertIsNone(user_info['nickname'])

    @patch('member.utils.social_utils.requests.get')
    def test_get_user_info_with_access_token_failed(self, mock_requests_get):
        # Given: Mock failed response from the requests.get method
        access_token = 'invalid_access_token'
        mock_response = Mock()
        mock_response.status_code = 401  # Unauthorized
        mock_requests_get.return_value = mock_response

        # When: Calling the get_user_info_with_access_token method with an invalid token
        # Then: It should raise a LoginFailedException
        with self.assertRaises(LoginFailedException):
            self.social_login_module.get_user_info_with_access_token(access_token)


class TestGoogleSocialLoginModule(TestCase):
    def setUp(self):
        self.social_login_module = GoogleSocialLoginModule()

    def test_initialize_google_social_login(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module._request_access_token_path, 'https://oauth2.googleapis.com/token')
        self.assertEqual(self.social_login_module._request_user_info_path, 'https://www.googleapis.com/oauth2/v3/userinfo')
        self.assertEqual(self.social_login_module._client_id, settings.GOOGLE_CLIENT_ID)
        self.assertEqual(self.social_login_module._secret, settings.GOOGLE_SECRET_KEY)
        self.assertEqual(self.social_login_module._redirect_uri, settings.GOOGLE_REDIRECT_URL)

    def test_request_access_token_path(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.request_access_token_path, 'https://oauth2.googleapis.com/token')

    def test_request_user_info_path(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.request_user_info_path, 'https://www.googleapis.com/oauth2/v3/userinfo')

    def test_client_id(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.client_id, settings.GOOGLE_CLIENT_ID)

    def test_secret(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.secret, settings.GOOGLE_SECRET_KEY)

    def test_redirect_uri(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.redirect_uri, settings.GOOGLE_REDIRECT_URL)

    def test_username_prefix(self):
        # Given:
        # Expected:
        self.assertEqual(self.social_login_module.username_prefix, 'google_')

    @patch('member.utils.social_utils.requests.get')
    def test_get_user_info_with_access_token_successful(self, mock_requests_get):
        # Given: Mock successful response from the requests.get method
        access_token = 'valid_access_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({
            'sub': '12345',
            'name': 'John Doe'
        })
        mock_requests_get.return_value = mock_response

        # When: Calling the get_user_info_with_access_token method
        user_info = self.social_login_module.get_user_info_with_access_token(access_token)

        # Then: The expected user information should be returned
        self.assertEqual(user_info['id'], 'google_12345')
        self.assertIsNone(user_info['gender'])
        self.assertIsNone(user_info['phone'])
        self.assertIsNone(user_info['birth'])
        self.assertIsNone(user_info['email'])
        self.assertEqual(user_info['name'], 'John Doe')
        self.assertIsNone(user_info['nickname'])

    @patch('member.utils.social_utils.requests.get')
    def test_get_user_info_with_access_token_failed(self, mock_requests_get):
        # Given: Mock failed response from the requests.get method
        access_token = 'invalid_access_token'
        mock_response = Mock()
        mock_response.status_code = 401  # Unauthorized
        mock_requests_get.return_value = mock_response

        # When: Calling the get_user_info_with_access_token method with an invalid token
        # Then: It should raise a LoginFailedException
        with self.assertRaises(LoginFailedException):
            self.social_login_module.get_user_info_with_access_token(access_token)


class TestSocialLoginHandler(TestCase):
    def setUp(self):
        self.social_login_handler = SocialLoginHandler(ExampleSocialLoginModule())

    def test_initialize_social_login_handler(self):
        # Given:
        # Expected:
        self.assertIsInstance(self.social_login_handler.social_module, SocialLoginModule)

    @patch('member.utils.social_utils.SocialLoginModule.get_access_token_by_code')
    @patch('member.utils.social_utils.SocialLoginModule.get_user_info_with_access_token')
    def test_validate(self, mock_get_user_info_with_access_token, mock_get_access_token_by_code):
        # Given:
        mock_get_access_token_by_code.return_value = 'valid_access_token'

        # When:
        self.social_login_handler.validate('valid_code')

        # Then:
        mock_get_access_token_by_code.once_called_with('valid_code')
        mock_get_user_info_with_access_token.once_called_with('valid_access_token')
