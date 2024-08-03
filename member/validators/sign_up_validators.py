from common.common_validators.validators import PayloadValidator
from member.consts import (
    MemberCreationExceptionMessage,
    NICKNAME_MAX_LENGTH,
    NICKNAME_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)
from member.services import (
    check_email_exists,
    check_email_reg_exp_valid,
    check_nickname_exists,
    check_nickname_valid,
    check_only_alphanumeric,
    check_only_korean_english_alphanumeric,
    check_username_exists,
)


class SignUpPayloadValidator(PayloadValidator):
    def __init__(self, payload: dict):
        super(SignUpPayloadValidator, self).__init__(payload)

    def validate(self) -> dict:
        # username
        if check_username_exists(self.payload['username']):
            self.add_error_context('username', MemberCreationExceptionMessage.USERNAME_EXISTS.label)
        if not (USERNAME_MIN_LENGTH <= len(self.payload['username']) <= USERNAME_MAX_LENGTH):
            self.add_error_context(
                'username',
                MemberCreationExceptionMessage.USERNAME_LENGTH_INVALID.label.format(
                    USERNAME_MIN_LENGTH,
                    USERNAME_MAX_LENGTH,
                )
            )
        if not check_only_alphanumeric(self.payload['username']):
            self.add_error_context(
                'username',
                MemberCreationExceptionMessage.USERNAME_REG_EXP_INVALID.label
            )

        # nickname
        if check_nickname_exists(self.payload['nickname']):
            self.add_error_context('nickname', MemberCreationExceptionMessage.NICKNAME_EXISTS.label)
        if not check_nickname_valid(self.payload['nickname']):
            self.add_error_context(
                'nickname',
                MemberCreationExceptionMessage.NICKNAME_BLACKLIST.label.format(
                    self.payload['nickname']
                )
            )
        if not (NICKNAME_MIN_LENGTH <= len(self.payload['nickname']) <= NICKNAME_MAX_LENGTH):
            self.add_error_context(
                'nickname',
                MemberCreationExceptionMessage.NICKNAME_LENGTH_INVALID.label.format(
                    NICKNAME_MIN_LENGTH,
                    NICKNAME_MAX_LENGTH,
                )
            )
        if not check_only_korean_english_alphanumeric(self.payload['nickname']):
            self.add_error_context(
                'nickname',
                MemberCreationExceptionMessage.NICKNAME_REG_EXP_INVALID.label
            )

        # email
        if check_email_exists(self.payload['email']):
            self.add_error_context('email', MemberCreationExceptionMessage.EMAIL_EXISTS.label)
        if not check_email_reg_exp_valid(self.payload['email']):
            self.add_error_context('email', MemberCreationExceptionMessage.EMAIL_REG_EXP_INVALID.label)

        # password
        if not (PASSWORD_MIN_LENGTH <= len(self.payload['password1']) <= PASSWORD_MAX_LENGTH):
            self.add_error_context(
                'password1',
                MemberCreationExceptionMessage.PASSWORD_LENGTH_INVALID.label.format(
                    PASSWORD_MIN_LENGTH,
                    PASSWORD_MAX_LENGTH,
                )
            )
        if self.payload['password1'] != self.payload['password2']:
            self.add_error_context('password2', MemberCreationExceptionMessage.CHECK_PASSWORD.label)

        if self.error_context:
            return self.error_context
        return {}
