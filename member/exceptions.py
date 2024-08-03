from common.common_exceptions import (
    CommonAPIException,
)


class LoginFailedException(CommonAPIException):
    status_code = 400
    default_detail = '로그인에 실패했습니다.'
    default_code = 'login-error'


class LoginRequiredException(CommonAPIException):
    status_code = 401
    default_detail = '로그인이 필요합니다.'
    default_code = 'login-required'


class NormalLoginFailedException(CommonAPIException):
    status_code = 400
    default_detail = '아이디 및 비밀번호 정보가 일치하지 않습니다.'
    default_code = 'invalid-username-or-password'


class SocialLoginTokenErrorException(CommonAPIException):
    status_code = 400
    default_detail = '소셜 로그인에 발급된 토큰에 문제가 있습니다.'
    default_code = 'social-token-error'


class InvalidRefreshTokenErrorException(CommonAPIException):
    status_code = 401
    default_detail = '잘못된 리프레시 토큰입니다.'
    default_code = 'invalid-refresh-token'


class InvalidValueForSignUpFieldErrorException(CommonAPIException):
    status_code = 400
    default_detail = '입력값을 다시 확인해주세요.'
    default_code = 'invalid-sign-up-field-value'


class SignUpEmailTokenErrorException(CommonAPIException):
    status_code = 400
    default_detail = '인증번호를 이메일로 전송하지 못했습니다.'
    default_code = 'sending-email-token-error'


class SignUpEmailTokenExpiredErrorException(CommonAPIException):
    status_code = 400
    default_detail = '이메일 인증번호를 다시 요청하세요.'
    default_code = 'email-token-expired'


class SignUpEmailTokenInvalidErrorException(CommonAPIException):
    status_code = 400
    default_detail = '인증번호가 다릅니다.'
    default_code = 'invalid-email-token'


class SignUpEmailTokenMacroErrorException(CommonAPIException):
    status_code = 400
    default_detail = '{}회 이상 인증번호를 틀리셨습니다. 현 이메일은 {}시간 동안 인증할 수 없습니다.'
    default_code = 'email-token-macro-error'


class MemberCreationErrorException(CommonAPIException):
    status_code = 400
    default_detail = '회원가입에 실패했습니다.'
    default_code = 'member-creation-fail'


class AlreadyMemberExistsErrorException(CommonAPIException):
    status_code = 400
    default_detail = '이미 가입된 회원입니다.'
    default_code = 'already-member-exists'


class BlackMemberException(CommonAPIException):
    status_code = 400
    default_detail = '정지된 유저입니다.'
    default_code = 'inaccessible-member-login'


class DormantMemberException(CommonAPIException):
    status_code = 400
    default_detail = '휴면상태의 유저입니다.'
    default_code = 'dormant-member-login'


class LeaveMemberException(CommonAPIException):
    status_code = 400
    default_detail = '탈퇴상태의 유저입니다.'
    default_code = 'leave-member-login'


class UnknownPlatformException(CommonAPIException):
    status_code = 400
    default_detail = '알 수 없는 로그인 방식입니다.'
    default_code = 'platform-error'
