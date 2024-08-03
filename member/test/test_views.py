from unittest.mock import (
    Mock,
    patch,
)

import jwt
from common.common_utils.error_utils import generate_pydantic_error_detail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from member.consts import (
    MemberCreationExceptionMessage,
    NICKNAME_MAX_LENGTH,
    NICKNAME_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    SIGNUP_MACRO_COUNT,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)
from member.dtos.request_dtos import SocialSignUpRequest
from member.models import (
    Guest,
    Member,
)
from pydantic import ValidationError


class SocialSignUpViewTestCase(TestCase):
    def setUp(self):
        self.member = Member.objects.create_user(username='test', nickname='test')
        self.url = reverse('member:social_sign_up')
        self.data = {
            'provider': 0,
            'token': 'test_token',
            'jobs_info': None,
        }

    @patch('member.views.Member.objects.get_or_create_member_by_token')
    @patch('member.views.get_jwt_login_token')
    @patch('member.views.get_jwt_refresh_token')
    def test_social_sign_up_should_success(self,
                                           mock_get_jwt_refresh_token,
                                           mock_get_jwt_login_token,
                                           mock_get_or_create_member_by_token):
        # Given: test data
        mock_get_jwt_login_token.return_value = 'test_access_token'
        mock_get_jwt_refresh_token.return_value = 'test_refresh_token'
        mock_get_or_create_member_by_token.return_value = (self.member, True)

        # When
        response = self.client.post(self.url, self.data, content_type='application/json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check the response data for expected keys
        self.assertEqual(response.data['access_token'], 'test_access_token')
        self.assertEqual(response.data['refresh_token'], 'test_refresh_token')
        mock_get_or_create_member_by_token.assert_called_once_with(
            self.data['token'],
            self.data['provider'],
        )
        self.assertEqual(
            Guest.objects.filter(member=self.member).exists(),
            True
        )
        mock_get_jwt_login_token.assert_called()
        mock_get_jwt_refresh_token.assert_called()

    @patch('member.views.Member.objects.get_or_create_member_by_token')
    @patch('member.views.get_jwt_login_token')
    @patch('member.views.get_jwt_refresh_token')
    def test_social_sign_up_should_success_with_job_info(self,
                                                         mock_get_jwt_refresh_token,
                                                         mock_get_jwt_login_token,
                                                         mock_get_or_create_member_by_token):
        # Given: test data
        mock_get_jwt_login_token.return_value = 'test_access_token'
        mock_get_jwt_refresh_token.return_value = 'test_refresh_token'
        mock_get_or_create_member_by_token.return_value = (self.member, True)

        # When
        response = self.client.post(self.url, self.data, content_type='application/json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check the response data for expected keys
        self.assertEqual(response.data['access_token'], 'test_access_token')
        self.assertEqual(response.data['refresh_token'], 'test_refresh_token')
        mock_get_or_create_member_by_token.assert_called_once_with(
            self.data['token'],
            self.data['provider'],
        )
        self.assertEqual(
            Guest.objects.filter(member=self.member).exists(),
            True
        )
        mock_get_jwt_login_token.assert_called()
        mock_get_jwt_refresh_token.assert_called()

    @patch('member.views.Member.objects.get_or_create_member_by_token')
    @patch('member.views.get_jwt_login_token')
    @patch('member.views.get_jwt_refresh_token')
    def test_social_sign_up_should_fail_when_already_exists_member(self,
                                                                   mock_get_jwt_refresh_token,
                                                                   mock_get_jwt_login_token,
                                                                   mock_get_or_create_member_by_token):
        # Given: test data
        mock_get_jwt_login_token.return_value = 'test_access_token'
        mock_get_jwt_refresh_token.return_value = 'test_refresh_token'
        # And: set the mock member as already exists
        mock_get_or_create_member_by_token.return_value = (self.member, False)

        # When
        response = self.client.post(self.url, self.data, content_type='application/json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 400)

        # Check the response data for expected keys
        self.assertEqual(response.data['message'], '이미 가입된 회원입니다.')
        self.assertEqual(response.data['error_code'], 'already-member-exists')
        self.assertEqual(response.data['errors'], None)
        mock_get_or_create_member_by_token.assert_called_once_with(
            self.data['token'],
            self.data['provider'],
        )
        mock_get_jwt_login_token.assert_not_called()
        mock_get_jwt_refresh_token.assert_not_called()

    @patch('member.views.Member.objects.get_or_create_member_by_token')
    @patch('member.views.get_jwt_login_token')
    @patch('member.views.get_jwt_refresh_token')
    @patch('member.views.SocialSignUpRequest.of')
    def test_social_sign_up_should_raise_error_when_pydantic_error(self,
                                                                   mock_of,
                                                                   mock_get_jwt_refresh_token,
                                                                   mock_get_jwt_login_token,
                                                                   mock_get_or_create_member_by_token):
        # Given:
        # And: Mock CreateProjectRequest.of to raise a Pydantic error
        mock_of.side_effect = ValidationError.from_exception_data(
            title=SocialSignUpRequest.__name__,
            line_errors=[
                generate_pydantic_error_detail(
                    'Error',
                    '에러',
                    'extra_information',
                    'ALL',
                )
            ]
        )

        # When
        response = self.client.post(self.url, self.data, content_type='application/json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 400)

        # Check the response data for expected keys
        self.assertEqual(response.data['message'], '입력값을 다시 한번 확인해주세요.')
        self.assertEqual(response.data['error_code'], '400-invalid_sign_up_input_data-00001')
        self.assertEqual(response.data['errors']['extra_information'], ['에러'])
        mock_get_or_create_member_by_token.assert_not_called()
        mock_get_jwt_login_token.assert_not_called()
        mock_get_jwt_refresh_token.assert_not_called()


class SocialLoginViewTestCase(TestCase):
    def setUp(self):
        self.member = Member.objects.create_user(username='test', nickname='test')
        self.guest = Guest.objects.create(
            member=self.member,
            temp_nickname='testsdfsdf',
            ip='127.0.0.1',
            email='test@test.com',
        )
        self.url = reverse('member:social_login')

    @patch('member.views.Member.objects.get_member_by_token')
    @patch('member.views.Member.raise_if_inaccessible')
    @patch('member.views.get_jwt_login_token')
    @patch('member.views.get_jwt_refresh_token')
    def test_social_login(self,
                          mock_get_jwt_refresh_token,
                          mock_get_jwt_login_token,
                          mock_raise_if_inaccessible,
                          get_member_by_token):
        # Given: test data
        data = {
            'provider': 0,
            'token': 'test_token',
        }
        mock_get_jwt_login_token.return_value = 'test_access_token'
        mock_get_jwt_refresh_token.return_value = 'test_refresh_token'
        get_member_by_token.return_value = self.member

        # When
        response = self.client.post(self.url, data, format='json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check the response data for expected keys
        mock_raise_if_inaccessible.called_once()
        self.assertEqual(response.data['access_token'], 'test_access_token')
        self.assertEqual(response.data['refresh_token'], 'test_refresh_token')
        self.assertEqual(
            Guest.objects.filter(member=self.member).exists(),
            True
        )

    @patch('member.views.Member.objects.get_member_by_token')
    @patch('member.views.Member.raise_if_inaccessible')
    @patch('member.views.get_jwt_login_token')
    @patch('member.views.get_jwt_refresh_token')
    def test_social_login_when_member_not_exists(self,
                                                 mock_get_jwt_refresh_token,
                                                 mock_get_jwt_login_token,
                                                 mock_raise_if_inaccessible,
                                                 get_member_by_token):
        # Given: test data
        data = {
            'provider': 0,
            'token': 'test_token',
        }
        mock_get_jwt_login_token.return_value = 'test_access_token'
        mock_get_jwt_refresh_token.return_value = 'test_refresh_token'
        get_member_by_token.return_value = None

        # When
        response = self.client.post(self.url, data, format='json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 400)

        # Check the response data for expected keys and values
        self.assertEqual(response.data['message'], '로그인에 실패했습니다.')
        self.assertEqual(response.data['error_code'], 'login-error')
        self.assertEqual(response.data['errors'], None)


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.member = Member.objects.all().first()
        self.url = reverse('member:normal_login')

    @patch('member.views.authenticate')
    @patch('member.views.get_jwt_login_token')
    @patch('member.views.get_jwt_refresh_token')
    def test_login_when_success(self, mock_get_jwt_refresh_token, mock_get_jwt_login_token, mock_authenticate):
        # Given: test data
        data = {
            'username': 'test_username',
            'password': 'test_password',
        }
        mock_get_jwt_login_token.return_value = 'test_access_token'
        mock_get_jwt_refresh_token.return_value = 'test_refresh_token'
        # And: set the mock member
        mock_authenticate.return_value = self.member

        # When
        response = self.client.post(self.url, data, format='json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check the response data for expected keys
        self.assertEqual(response.data['access_token'], 'test_access_token')
        self.assertEqual(response.data['refresh_token'], 'test_refresh_token')

    @patch('member.views.authenticate')
    def test_login_when_fail_with_not_member_exists(self, mock_authenticate):
        # Given: test data
        data = {
            'username': 'test_username',
            'password': 'test_password',
        }
        # And: set the mock member as None
        mock_authenticate.return_value = None

        # When
        response = self.client.post(self.url, data, format='json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 400)

        # Check the response data for expected keys
        self.assertEqual(response.data['message'], '아이디 및 비밀번호 정보가 일치하지 않습니다.')
        self.assertEqual(response.data['error_code'], 'invalid-username-or-password')


class RefreshTokenViewViewTestCase(TestCase):
    def setUp(self):
        self.member = Member.objects.all().first()
        self.url = reverse('member:refresh_token')

    @patch('member.views.jwt_decode_handler')
    @patch('member.views.get_jwt_refresh_token')
    @patch('member.views.get_jwt_login_token')
    def test_refresh_token_when_success(self, mock_get_jwt_login_token, mock_get_jwt_refresh_token, mock_jwt_decode_handler):
        # Given: test data
        data = {
            'refresh_token': 'test_refresh_token',
        }
        mock_jwt_decode_handler.return_value = {
            'member_id': self.member.id,
        }
        mock_get_jwt_login_token.return_value = 'test_jwt_login_token'
        mock_get_jwt_refresh_token.return_value = 'test_jwt_refresh_token'

        # When
        response = self.client.post(self.url, data, format='json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check the response data for expected keys
        self.assertEqual(response.data['access_token'], 'test_jwt_login_token')
        self.assertEqual(response.data['refresh_token'], 'test_jwt_refresh_token')

    @patch('member.views.jwt_decode_handler')
    def test_refresh_token_fail_with_member_not_exists(self, mock_jwt_decode_handler):
        # Given: test data
        data = {
            'refresh_token': 'test_refresh_token',
        }
        # And: set the mock member as not exists
        mock_jwt_decode_handler.return_value = {
            'member_id': 0,
        }

        # When
        response = self.client.post(self.url, data, format='json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 401)

        # Check the response data for expected keys
        self.assertEqual(response.data['message'], '잘못된 리프레시 토큰입니다.')

    @patch('member.views.jwt_decode_handler')
    def test_refresh_token_fail_with_jwt_invalid(self, mock_jwt_decode_handler):
        # Given: test data
        data = {
            'refresh_token': 'test_refresh_token',
        }
        # And: set the mock member as not exists
        mock_jwt_decode_handler.side_effect = jwt.InvalidTokenError('test_exception')

        # When
        response = self.client.post(self.url, data, format='json')

        # Then
        # Check the response status code
        self.assertEqual(response.status_code, 401)

        # Check the response data for expected keys
        self.assertEqual(response.data['message'], '잘못된 리프레시 토큰입니다.')


class SignUpEmailTokenSendTestCase(TestCase):
    def setUp(self):
        super(SignUpEmailTokenSendTestCase, self).setUp()
        self.body = {
            'username': 'test',
            'nickname': 'test_token',
            'password2': '12341234123412341234',
            'email': 'aaaa@naver.com',
        }

    @patch('member.views.send_one_time_token_email')
    @patch('member.views.get_cache_value_by_key')
    @patch('member.views.generate_random_string_digits')
    def test_email_token_create_when_token_create_successful(self, mock_generate_random_string_digits, mock_get_cache_value_by_key, mock_send_one_time_token_email):
        # Given:
        mock_generate_random_string_digits.return_value = '1234'
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': mock_generate_random_string_digits.return_value,
            'email': self.body['email'],
            'username': self.body['username'],
            'nickname': self.body['nickname'],
            'password2': self.body['password2'],
        }

        # When:
        response = self.client.post(reverse('member:sign_up_check'), self.body)

        # Then: 성공 했다는 메시지 반환
        self.assertEqual(response.status_code, 200)
        mock_send_one_time_token_email.apply_async.assert_called_once_with(
            (
                self.body['email'],
                mock_get_cache_value_by_key.return_value['one_time_token'],
            )
        )
        self.assertEqual(response.data['message'], '인증번호를 이메일로 전송했습니다.')
        # And: cache 에 값이 저장되었는지 확인
        self.assertDictEqual(cache.get(self.body['email']), mock_get_cache_value_by_key.return_value)

    @patch('member.views.generate_dict_value_by_key_to_cache', Mock())
    @patch('member.views.send_one_time_token_email')
    @patch('member.views.get_cache_value_by_key')
    def test_email_token_create_when_token_create_failed(self, mock_get_cache_value_by_key, mock_send_one_time_token_email):
        # Given:
        mock_get_cache_value_by_key.return_value = None

        # When:
        response = self.client.post(reverse('member:sign_up_check'), self.body)

        # Then: 실패 했다는 메시지 반환
        self.assertEqual(response.status_code, 400)
        mock_send_one_time_token_email.assert_not_called()
        self.assertEqual(response.data['message'], '인증번호를 이메일로 전송하지 못했습니다.')


class SignUpEmailTokenValidationEndViewTestCase(TestCase):
    def setUp(self):
        super(SignUpEmailTokenValidationEndViewTestCase, self).setUp()
        self.body = {
            'email': 'aaaa@naver.com',
            'one_time_token': '1234',
        }

    @patch('member.views.increase_cache_int_value_by_key')
    def test_email_token_validate_should_return_fail_when_macro_count_is_30_times(self, mock_increase_cache_int_value_by_key):
        # Given: 30 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 30

        # When:
        response = self.client.post(reverse('member:sign_up_token_validation'), self.body)

        # Then: 메크로 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['message'],
            '{}회 이상 인증번호를 틀리셨습니다. 현 이메일은 {}시간 동안 인증할 수 없습니다.'.format(SIGNUP_MACRO_COUNT, 24)
        )

    @patch('member.views.increase_cache_int_value_by_key')
    @patch('member.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_email_key_not_exists(self,
                                                                               mock_get_cache_value_by_key,
                                                                               mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        # And: 인증한 이메일이 없는 경우
        mock_get_cache_value_by_key.return_value = None

        # When:
        response = self.client.post(reverse('member:sign_up_token_validation'), self.body)

        # Then: 이메일 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['message'],
            '이메일 인증번호를 다시 요청하세요.',
        )

    @patch('member.views.increase_cache_int_value_by_key')
    @patch('member.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_one_time_token_not_exists(self,
                                                                                    mock_get_cache_value_by_key,
                                                                                    mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        # And: one time token 이 없는 경우
        mock_get_cache_value_by_key.return_value = {
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }

        # When:
        response = self.client.post(reverse('member:sign_up_token_validation'), self.body)

        # Then: 인증번호 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['message'],
            '인증번호가 다릅니다.',
        )
        self.assertEqual(
            response.data['errors']['one_time_token'][0],
            '인증번호가 다릅니다.',
        )

    @patch('member.views.increase_cache_int_value_by_key')
    @patch('member.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_one_time_token_is_different(self,
                                                                                      mock_get_cache_value_by_key,
                                                                                      mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        # And: one time token 다르게 설정
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1233',
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }
        # And: one time token 다르게 설정
        self.body['one_time_token'] = '1234'

        # When:
        response = self.client.post(reverse('member:sign_up_token_validation'), self.body)

        # Then: 인증번호 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['message'],
            '인증번호가 다릅니다.',
        )

    @patch('member.views.increase_cache_int_value_by_key')
    @patch('member.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_username_user_already_exists(self,
                                                                                       mock_get_cache_value_by_key,
                                                                                       mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1234',
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }
        # And: 이미 username mocking 한 데이터의 계정이 있는 경우
        Member.objects.create_user(username='test')

        # When:
        response = self.client.post(reverse('member:sign_up_token_validation'), self.body)

        # Then: username 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['message'],
            MemberCreationExceptionMessage.USERNAME_EXISTS.label,
        )

    @patch('member.views.increase_cache_int_value_by_key')
    @patch('member.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_nickname_user_already_exists(self,
                                                                                       mock_get_cache_value_by_key,
                                                                                       mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1234',
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }
        # And: 이미 nickname mocking 한 데이터의 계정이 있는 경우
        Member.objects.create_user(username='test2', nickname='test')

        # When:
        response = self.client.post(reverse('member:sign_up_token_validation'), self.body)

        # Then: 닉네임 중복 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['message'],
            MemberCreationExceptionMessage.NICKNAME_EXISTS.label,
        )

    @patch('member.views.increase_cache_int_value_by_key')
    @patch('member.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_email_user_already_exists(self,
                                                                                    mock_get_cache_value_by_key,
                                                                                    mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1234',
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }
        # And: 이미 email mocking 한 데이터의 계정이 있는 경우
        Member.objects.create_user(username='test2', nickname='test2', email='test@test.com')

        # When:
        response = self.client.post(reverse('member:sign_up_token_validation'), self.body)

        # Then: email 중복 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['message'],
            MemberCreationExceptionMessage.EMAIL_EXISTS.label,
        )

    @patch('member.views.delete_cache_value_by_key', Mock())
    @patch('member.views.increase_cache_int_value_by_key')
    @patch('member.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_success(self,
                                                        mock_get_cache_value_by_key,
                                                        mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1234',
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }

        # When:
        response = self.client.post(reverse('member:sign_up_token_validation'), self.body)

        # Then: 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['message'],
            '회원가입에 성공했습니다.',
        )
        self.assertEqual(
            Member.objects.filter(email=mock_get_cache_value_by_key.return_value['email']).exists(),
            True
        )
        self.assertEqual(
            Guest.objects.filter(email=mock_get_cache_value_by_key.return_value['email']).exists(),
            True,
        )


class SignUpValidationTestCase(TestCase):
    def setUp(self):
        super(SignUpValidationTestCase, self).setUp()
        self.body = {
            'username': 'testtest',
            'nickname': 'testto',
            'password1': '12341234123412341234',
            'password2': '12341234123412341234',
            'email': 'aaaa@naver.com',
            'one_time_token': '1234',
        }

    def test_sign_up_validation_success(self):
        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'success')

    def test_sign_up_validation_should_fail_when_email_regexp_is_not_valid(self):
        self.body['email'] = 'something'

        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: email 문제로 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors']['email'][0], MemberCreationExceptionMessage.EMAIL_REG_EXP_INVALID.label)

    def test_sign_up_validation_should_fail_when_username_length_is_invalid(self):
        # Given: username 길이 설정
        self.body['username'] = 'a'

        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: username 길이 문제로 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['errors']['username'][0],
            MemberCreationExceptionMessage.USERNAME_LENGTH_INVALID.label.format(
                USERNAME_MIN_LENGTH,
                USERNAME_MAX_LENGTH,
            )
        )

    def test_sign_up_validation_should_fail_when_username_regexp_is_invalid(self):
        # Given: username 한글 설정
        self.body['username'] = '한글'

        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: username 글자 문제로 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            MemberCreationExceptionMessage.USERNAME_REG_EXP_INVALID.label,
            response.data['errors']['username'],
        )

    def test_sign_up_validation_should_fail_when_nickname_length_is_invalid(self):
        # Given: nickname 길이 설정
        self.body['nickname'] = 'a'

        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: nickname 길이 문제로 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['errors']['nickname'][0],
            MemberCreationExceptionMessage.NICKNAME_LENGTH_INVALID.label.format(
                NICKNAME_MIN_LENGTH,
                NICKNAME_MAX_LENGTH,
            )
        )

    def test_sign_up_validation_should_fail_when_nickname_regex_is_invalid(self):
        # Given: nickname 특수 문자 설정
        self.body['nickname'] = '특수문자!@#$%^&*()'

        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: nickname 글자 문제로 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            MemberCreationExceptionMessage.NICKNAME_REG_EXP_INVALID.label,
            response.data['errors']['nickname'],
        )

    def test_sign_up_validation_should_fail_when_username_already_exists(self):
        # Given: 유저를 생성
        Member.objects.create_user(username='test')
        # And: username 중복 설정
        self.body['username'] = 'test'

        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: username 중복 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors']['username'][0], MemberCreationExceptionMessage.USERNAME_EXISTS.label)

    def test_sign_up_validation_should_fail_when_nickname_already_exists(self):
        # Given: 유저를 생성
        Member.objects.create_user(username='test2', nickname='test_token')
        # And: nickname 중복 설정
        self.body['nickname'] = 'test_token'

        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: nickname 중복 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors']['nickname'][0], MemberCreationExceptionMessage.NICKNAME_EXISTS.label)

    def test_sign_up_validation_should_fail_when_email_already_exists(self):
        # Given: 유저를 생성
        Member.objects.create_user(username='test3', nickname='tes2t_token22', email='aaaa@naver.com')
        # And: 중복 닉네임 설정
        self.body['email'] = 'aaaa@naver.com'

        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: nickname 중복 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors']['email'][0], MemberCreationExceptionMessage.EMAIL_EXISTS.label)

    def test_sign_up_validation_should_fail_when_password_wrong(self):
        # Given: 비밀번호 다르게 설정
        self.body['password2'] = '12312312'

        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: password 확인 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors']['password2'][0], MemberCreationExceptionMessage.CHECK_PASSWORD.label)

    def test_sign_up_validation_should_fail_when_password_length_is_invalid(self):
        # Given: password1 길이 설정
        self.body['password1'] = 'a'

        # When: 회원가입 검증 요청
        response = self.client.post(reverse('member:sign_up_validation'), self.body)

        # Then: password1 길이 문제로 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['errors']['password1'][0],
            MemberCreationExceptionMessage.PASSWORD_LENGTH_INVALID.label.format(
                PASSWORD_MIN_LENGTH,
                PASSWORD_MAX_LENGTH,
            )
        )


class GetOrCreateGuestTokenViewTestCase(TestCase):
    def setUp(self):
        super(GetOrCreateGuestTokenViewTestCase, self).setUp()

    @patch('member.views.get_jwt_refresh_token')
    @patch('member.views.get_jwt_guest_token')
    @patch('member.views.get_request_ip')
    def test_guest_ip_exists(self,
                             mock_get_request_ip,
                             mock_get_jwt_guest_token,
                             mock_get_jwt_refresh_token):
        # Given:
        guest = Guest.objects.first()
        mock_get_request_ip.return_value = guest.ip
        mock_get_jwt_guest_token.return_value = 'test_guest_token'
        mock_get_jwt_refresh_token.return_value = 'test_refresh_token'

        # When: Guest Token Request
        response = self.client.post(reverse('member:guest_token'))

        # Then:
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.data,
            {
                'access_token': 'test_guest_token',
                'refresh_token': 'test_refresh_token',
            }
        )
        mock_get_jwt_guest_token.called_once_with(guest)
        mock_get_jwt_refresh_token.called_once_with(guest)

    @patch('member.views.get_jwt_refresh_token')
    @patch('member.views.get_jwt_guest_token')
    @patch('member.views.get_request_ip')
    def test_guest_ip_not_exists(self,
                                 mock_get_request_ip,
                                 mock_get_jwt_guest_token,
                                 mock_get_jwt_refresh_token):
        # Given:
        self.assertEqual(
            Guest.objects.filter(ip='111.111.111.111').exists(),
            False,
        )
        mock_get_request_ip.return_value = '111.111.111.111'
        mock_get_jwt_guest_token.return_value = 'test_guest_token'
        mock_get_jwt_refresh_token.return_value = 'test_refresh_token'

        # When: Guest Token Request
        response = self.client.post(reverse('member:guest_token'))

        # Then:
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.data,
            {
                'access_token': 'test_guest_token',
                'refresh_token': 'test_refresh_token',
            }
        )
        guest = Guest.objects.get(ip='111.111.111.111')
        mock_get_jwt_guest_token.called_once_with(guest)
        mock_get_jwt_refresh_token.called_once_with(guest)
