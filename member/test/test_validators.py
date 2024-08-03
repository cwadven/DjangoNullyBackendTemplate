from unittest.mock import patch

from django.test import TestCase
from member.consts import (
    MemberCreationExceptionMessage,
    NICKNAME_MAX_LENGTH,
    NICKNAME_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)
from member.validators.sign_up_validators import SignUpPayloadValidator


class SignUpPayloadValidatorTest(TestCase):
    def setUp(self):
        self.valid_payload = {
            "username": "validusername",
            "nickname": "valid",
            "email": "valid@example.com",
            "password1": "validpassword123",
            "password2": "validpassword123",
        }

    def test_validate_with_valid_payload(self):
        # Given:
        # When:
        validator = SignUpPayloadValidator(self.valid_payload)
        errors = validator.validate()

        # Then:
        self.assertDictEqual(errors, {})

    @patch('member.validators.sign_up_validators.check_username_exists')
    def test_validate_with_already_exists_username(self, mock_check_username_exists):
        # Given: check_username_exists 함수를 임시로 True 로 설정
        mock_check_username_exists.return_value = True

        # When:
        validator = SignUpPayloadValidator(self.valid_payload)
        errors = validator.validate()

        # Then:
        self.assertIn('username', errors)
        self.assertEqual(errors['username'], [MemberCreationExceptionMessage.USERNAME_EXISTS.label])

    def test_validate_with_invalid_username_length(self):
        # Given: 유효하지 않은 username 길이
        invalid_lengths = [USERNAME_MIN_LENGTH - 1, USERNAME_MAX_LENGTH + 1]

        for invalid_length in invalid_lengths:
            self.valid_payload['username'] = 'a' * invalid_length

            # When:
            validator = SignUpPayloadValidator(self.valid_payload)
            errors = validator.validate()

            # Then:
            self.assertIn('username', errors)
            self.assertEqual(
                errors['username'],
                [
                    MemberCreationExceptionMessage.USERNAME_LENGTH_INVALID.label.format(
                        USERNAME_MIN_LENGTH,
                        USERNAME_MAX_LENGTH,
                    )
                ]
            )

    @patch('member.validators.sign_up_validators.check_only_alphanumeric')
    def test_validate_with_invalid_username_check_only_alphanumeric(self, mock_check_only_alphanumeric):
        # Given: check_only_alphanumeric 함수를 임시로 False 로 설정
        mock_check_only_alphanumeric.return_value = False

        # When:
        validator = SignUpPayloadValidator(self.valid_payload)
        errors = validator.validate()

        # Then:
        self.assertIn('username', errors)
        self.assertEqual(errors['username'], [MemberCreationExceptionMessage.USERNAME_REG_EXP_INVALID.label])

    @patch('member.validators.sign_up_validators.check_nickname_exists')
    def test_validate_with_nickname_when_already_exists(self, mock_check_nickname_exists):
        # Given: check_nickname_exists 함수를 임시로 True 로 설정
        mock_check_nickname_exists.return_value = True

        # When:
        validator = SignUpPayloadValidator(self.valid_payload)
        errors = validator.validate()

        # Then:
        self.assertIn('nickname', errors)
        self.assertEqual(errors['nickname'], [MemberCreationExceptionMessage.NICKNAME_EXISTS.label])

    @patch('member.validators.sign_up_validators.check_nickname_valid')
    def test_validate_with_nickname_when_invalid_word(self, mock_check_nickname_valid):
        # Given: check_nickname_valid 함수를 임시로 False 로 설정
        mock_check_nickname_valid.return_value = False

        # When:
        validator = SignUpPayloadValidator(self.valid_payload)
        errors = validator.validate()

        # Then:
        self.assertIn('nickname', errors)
        self.assertEqual(
            errors['nickname'],
            [MemberCreationExceptionMessage.NICKNAME_BLACKLIST.label.format(self.valid_payload['nickname'])]
        )

    def test_validate_with_invalid_nickname_length(self):
        # Given: 유효하지 않은 nickname 길이
        invalid_lengths = [NICKNAME_MIN_LENGTH - 1, NICKNAME_MAX_LENGTH + 1]

        for invalid_length in invalid_lengths:
            self.valid_payload['nickname'] = 'a' * invalid_length

            # When:
            validator = SignUpPayloadValidator(self.valid_payload)
            errors = validator.validate()

            # Then:
            self.assertIn('nickname', errors)
            self.assertEqual(
                errors['nickname'],
                [
                    MemberCreationExceptionMessage.NICKNAME_LENGTH_INVALID.label.format(
                        NICKNAME_MIN_LENGTH,
                        NICKNAME_MAX_LENGTH,
                    )
                ]
            )

    @patch('member.validators.sign_up_validators.check_only_korean_english_alphanumeric')
    def test_validate_with_invalid_nickname_check_only_korean_english_alphanumeric(self, mock_check_only_korean_english_alphanumeric):
        # Given: check_only_korean_english_alphanumeric 함수를 임시로 False 로 설정
        mock_check_only_korean_english_alphanumeric.return_value = False

        # When:
        validator = SignUpPayloadValidator(self.valid_payload)
        errors = validator.validate()

        # Then:
        self.assertIn('nickname', errors)
        self.assertEqual(errors['nickname'], [MemberCreationExceptionMessage.NICKNAME_REG_EXP_INVALID.label])

    @patch('member.validators.sign_up_validators.check_email_exists')
    def test_validate_with_email_when_already_exists(self, mock_check_email_exists):
        # Given: check_email_exists 함수를 임시로 True 로 설정
        mock_check_email_exists.return_value = True

        # When:
        validator = SignUpPayloadValidator(self.valid_payload)
        errors = validator.validate()

        # Then:
        self.assertIn('email', errors)
        self.assertEqual(errors['email'], [MemberCreationExceptionMessage.EMAIL_EXISTS.label])

    @patch('member.validators.sign_up_validators.check_email_reg_exp_valid')
    def test_validate_with_invalid_email_check_only_korean_english_alphanumeric(self, mock_check_email_reg_exp_valid):
        # Given: check_email_reg_exp_valid 함수를 임시로 False 로 설정
        mock_check_email_reg_exp_valid.return_value = False

        # When:
        validator = SignUpPayloadValidator(self.valid_payload)
        errors = validator.validate()

        # Then:
        self.assertIn('email', errors)
        self.assertEqual(errors['email'], [MemberCreationExceptionMessage.EMAIL_REG_EXP_INVALID.label])

    def test_validate_with_invalid_password_length(self):
        # Given: 유효하지 않은 password 길이
        invalid_lengths = [PASSWORD_MIN_LENGTH - 1, PASSWORD_MAX_LENGTH + 1]

        for invalid_length in invalid_lengths:
            self.valid_payload['password1'] = 'a' * invalid_length

            # When:
            validator = SignUpPayloadValidator(self.valid_payload)
            errors = validator.validate()

            # Then:
            self.assertIn('password1', errors)
            self.assertEqual(
                errors['password1'],
                [
                    MemberCreationExceptionMessage.PASSWORD_LENGTH_INVALID.label.format(
                        PASSWORD_MIN_LENGTH,
                        PASSWORD_MAX_LENGTH,
                    )
                ]
            )

    def test_validate_with_invalid_password1_and_password2_word_equal(self):
        # Given: 비밀번호 다르게 설정
        self.valid_payload['password1'] = 'valid'
        self.valid_payload['password2'] = 'invalid'

        # When:
        validator = SignUpPayloadValidator(self.valid_payload)
        errors = validator.validate()

        # Then:
        self.assertIn('password2', errors)
        self.assertEqual(errors['password2'], [MemberCreationExceptionMessage.CHECK_PASSWORD.label])
