from datetime import datetime
from unittest.mock import patch

from common.common_utils.token_utils import (
    get_jwt_guest_token,
    get_jwt_login_token,
    get_jwt_refresh_token,
    jwt_payload_handler,
)
from django.contrib.auth import get_user_model
from django.test import TestCase
from freezegun import freeze_time
from member.models import Guest
from rest_framework_jwt.settings import api_settings


class TestGetJWTLoginToken(TestCase):
    def setUp(self):
        self.guest = Guest.objects.all().first()

    @patch('common.common_utils.token_utils.jwt_payload_handler')
    @patch('common.common_utils.token_utils.jwt_encode_handler')
    def test_get_jwt_login_token(self, mock_jwt_encode_handler, mock_jwt_payload_handler):
        # Given:
        # When:
        get_jwt_login_token(self.guest.member)

        # Then: Ensure the function executes and returns the expected result
        mock_jwt_payload_handler.assert_called_once_with(self.guest)
        mock_jwt_encode_handler.assert_called_once_with(mock_jwt_payload_handler.return_value)


class TestGetJwtGuestToken(TestCase):
    def setUp(self):
        self.guest = Guest.objects.all().first()

    @patch('common.common_utils.token_utils.jwt_payload_handler')
    @patch('common.common_utils.token_utils.jwt_encode_handler')
    def test_get_jwt_guest_token(self, mock_jwt_encode_handler, mock_jwt_payload_handler):
        # Given:
        # When:
        get_jwt_guest_token(self.guest)

        # Then: Ensure the function executes and returns the expected result
        mock_jwt_payload_handler.assert_called_once_with(self.guest)
        mock_jwt_encode_handler.assert_called_once_with(mock_jwt_payload_handler.return_value)


class TestGetJWTRefreshToken(TestCase):
    def setUp(self):
        self.guest = Guest.objects.all().first()

    @freeze_time('2020-01-01 00:00:00')
    @patch('common.common_utils.token_utils.jwt_encode_handler')
    def test_get_jwt_refresh_token(self, mock_jwt_encode_handler):
        # Given:
        # When:
        get_jwt_refresh_token(self.guest)

        # Then: Ensure the function executes and returns the expected result
        mock_jwt_encode_handler.assert_called_once_with({
            'guest_id': self.guest.id,
            'member_id': self.guest.member.id,
            'exp': datetime(2020, 1, 8)
        })


class JWTPayloadHandlerTest(TestCase):
    def setUp(self):
        self.UserModel = get_user_model()
        self.guest = Guest.objects.all().first()

    @freeze_time('2020-01-01 00:00:00')
    def test_jwt_payload_handler_with_standard_user(self):
        # When:
        payload = jwt_payload_handler(self.guest)

        # Then:
        self.assertDictEqual(
            payload,
            {
                'guest_id': self.guest.id,
                'member_id': self.guest.member.id,
                'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA,
            }
        )
