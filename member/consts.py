from common.common_consts.common_enums import (
    IntValueSelector,
    StrValueLabel,
)
from member.exceptions import (
    BlackMemberException,
    DormantMemberException,
    LeaveMemberException,
    UnknownPlatformException,
)
from member.utils.social_utils import (
    GoogleSocialLoginModule,
    KakaoSocialLoginModule,
    NaverSocialLoginModule,
)


class SocialLoginModuleSelector(IntValueSelector):
    """
    데이터베이스에 2, 3, 4 로 MemberProvider 와 의미가 같아야 합니다.
    """
    KAKAO = (2, KakaoSocialLoginModule)
    NAVER = (3, NaverSocialLoginModule)
    GOOGLE = (4, GoogleSocialLoginModule)

    @classmethod
    def _missing_(cls, value):
        raise UnknownPlatformException()


class MemberStatusExceptionTypeSelector(IntValueSelector):
    """
    데이터베이스에 2, 3, 4 로 MemberStatus 와 의미가 같아야 합니다.
    """
    LEAVE_MEMBER_EXCEPTION = (2, LeaveMemberException)
    BLACK_MEMBER_EXCEPTION = (3, BlackMemberException)
    DORMANT_MEMBER_EXCEPTION = (4, DormantMemberException)


class MemberCreationExceptionMessage(StrValueLabel):
    USERNAME_EXISTS = ('already-exists-username', '이미 사용중인 아이디입니다.')
    USERNAME_LENGTH_INVALID = ('username-length-invalid', '아이디는 {}자 이상 {}자 이하로 입력해주세요.')
    USERNAME_REG_EXP_INVALID = ('username-reg-exp-invalid', '아이디는 영문, 숫자만 입력 가능합니다.')
    NICKNAME_EXISTS = ('already-exists-nickname', '이미 사용중인 닉네임입니다.')
    NICKNAME_LENGTH_INVALID = ('nickname-length-invalid', '닉네임은 {}자 이상 {}자 이하로 입력해주세요.')
    NICKNAME_REG_EXP_INVALID = ('nickname-reg-exp-invalid', '닉네임은 한글, 영문, 숫자만 입력 가능합니다.')
    NICKNAME_BLACKLIST = ('nickname-black-list', '{} 는 사용할 수 없는 닉네임입니다.')
    EMAIL_EXISTS = ('already-exists-email', '이미 가입한 이메일입니다.')
    CHECK_PASSWORD = ('check-password', '비밀번호와 비밀번호 확인이 동일하지 않습니다.')
    PASSWORD_LENGTH_INVALID = ('password-length-invalid', '비밀번호는 {}자 이상 {}자 이하로 입력해주세요.')
    EMAIL_REG_EXP_INVALID = ('email-reg-exp-invalid', '이메일 형식이 올바르지 않습니다.')


class MemberProviderEnum(IntValueSelector):
    """
    상수 값으로 Member Provider 제어하기
    """
    EMAIL = (1, 'email')
    KAKAO = (2, 'kakao')
    NAVER = (3, 'naver')
    GOOGLE = (4, 'google')


class MemberTypeEnum(IntValueSelector):
    """
    상수 값으로 Member Type 제어하기
    """
    SYSTEM_ADMIN = (1, '관리자')
    PRODUCT_ADMIN = (2, '운영자')
    NORMAL_MEMBER = (3, '일반')


class MemberStatusEnum(IntValueSelector):
    """
    데이터베이스에 1, 2, 3, 4 로 MemberStatus 와 의미가 같아야 합니다.
    """
    NORMAL_MEMBER = (1, '정상')
    LEAVE_MEMBER = (2, '탈퇴')
    BLACK_MEMBER = (3, '정지')
    DORMANT_MEMBER = (4, '휴면')


SIGNUP_MACRO_VALIDATION_KEY = '{}:signup:count'
SIGNUP_MACRO_COUNT = 30
SIGNUP_MACRO_EXPIRE_SECONDS = 60 * 60 * 24
SIGNUP_EMAIL_TOKEN_TTL = 60 * 5

USERNAME_MIN_LENGTH = 4
USERNAME_MAX_LENGTH = 16

NICKNAME_MIN_LENGTH = 2
NICKNAME_MAX_LENGTH = 8

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 30
