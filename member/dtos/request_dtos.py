from datetime import date
from typing import (
    List,
    Optional,
)

from common.common_consts.common_error_messages import ErrorMessage
from django.http import QueryDict
from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class NormalLoginRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)


class SocialLoginRequest(BaseModel):
    token: str = Field(...)
    provider: int = Field(...)


class SocialSignUpJobInfo(BaseModel):
    job_id: int = Field(...)
    start_date: date = Field(...)
    end_date: Optional[date] = Field(...)


class SocialSignUpRequest(BaseModel):
    token: str = Field(description='외부 로그인 토큰')
    provider: int = Field(description='외부 로그인 제공자')
    jobs_info: Optional[List[SocialSignUpJobInfo]] = Field(description='회원 직군 정보')

    @field_validator(
        'jobs_info',
        mode='before'
    )
    def check_jobs_value(cls, v):
        if v is None:
            return None

        if not len(v):
            raise ValueError(ErrorMessage.INVALID_MINIMUM_ITEM_SIZE.label.format(1))

        for job_info in v:
            if set(job_info.keys()) != {'job_id', 'start_date', 'end_date'}:
                raise ValueError(ErrorMessage.INVALID_INPUT_ERROR_MESSAGE.label)
        return v

    @classmethod
    def of(cls, request: QueryDict):
        return cls(
            **request
        )


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(...)


class SignUpEmailTokenSendRequest(BaseModel):
    email: str = Field(...)
    username: str = Field(...)
    nickname: str = Field(...)
    password2: str = Field(...)


class SignUpEmailTokenValidationEndRequest(BaseModel):
    email: str = Field(...)
    one_time_token: str = Field(...)


class SignUpValidationRequest(BaseModel):
    username: str = Field(...)
    nickname: str = Field(...)
    email: str = Field(...)
    password1: str = Field(...)
    password2: str = Field(...)
