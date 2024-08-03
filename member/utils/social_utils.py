import json
from abc import (
    ABC,
    abstractmethod,
)
from datetime import datetime
from typing import Optional
from urllib.parse import unquote

import requests
from django.conf import settings
from member.exceptions import (
    LoginFailedException,
    SocialLoginTokenErrorException,
)


class SocialLoginModule(ABC):
    _request_access_token_path = None
    _request_user_info_path = None
    _client_id = None
    _secret = None
    _redirect_uri = None
    _username_prefix = None

    @property
    @abstractmethod
    def request_access_token_path(self) -> str:
        pass

    @property
    @abstractmethod
    def request_user_info_path(self) -> str:
        pass

    @property
    @abstractmethod
    def client_id(self) -> str:
        pass

    @property
    @abstractmethod
    def secret(self) -> str:
        pass

    @property
    @abstractmethod
    def redirect_uri(self) -> str:
        pass

    @property
    @abstractmethod
    def username_prefix(self) -> str:
        pass

    @abstractmethod
    def get_user_info_with_access_token(self, access_token: str) -> dict:
        pass

    def get_access_token_by_code(self, code: str) -> str:
        access_data = requests.post(
            self.request_access_token_path,
            data={
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.secret,
                'redirect_uri': self.redirect_uri,
                'code': unquote(code)
            }
        )
        if access_data.status_code != 200:
            raise LoginFailedException()

        try:
            return json.loads(access_data.text)['access_token']
        except KeyError:
            raise SocialLoginTokenErrorException()


class KakaoSocialLoginModule(SocialLoginModule):
    def __init__(self):
        self._request_access_token_path = 'https://kauth.kakao.com/oauth/token'
        self._request_user_info_path = 'https://kapi.kakao.com/v2/user/me'
        self._client_id = settings.KAKAO_API_KEY
        self._secret = settings.KAKAO_SECRET_KEY
        self._redirect_uri = settings.KAKAO_REDIRECT_URL
        self._username_prefix = 'kakao_'

    @property
    def request_access_token_path(self) -> str:
        return self._request_access_token_path

    @property
    def request_user_info_path(self) -> str:
        return self._request_user_info_path

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def secret(self) -> str:
        return self._secret

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    @property
    def username_prefix(self) -> str:
        return self._username_prefix

    @staticmethod
    def _get_birth_day(data: dict) -> Optional[datetime]:
        try:
            birth = data['kakao_account']['birthyear'] + data['kakao_account']['birthday']
            return datetime.strptime(birth, '%Y%m%d')
        except (KeyError, ValueError):
            return

    @staticmethod
    def _get_gender(data: dict) -> Optional[str]:
        try:
            return data['kakao_account']['gender']
        except KeyError:
            return

    @staticmethod
    def _get_phone(data: dict) -> Optional[str]:
        try:
            return data['kakao_account']['phone_number'].replace(
                '+82 ',
                '0'
            ).replace(
                '-',
                ''
            ).replace(
                ' ',
                '',
            )
        except KeyError:
            return

    @staticmethod
    def _get_email(data: dict) -> Optional[str]:
        try:
            return data['kakao_account']['email']
        except KeyError:
            return

    @staticmethod
    def _get_name(data: dict) -> Optional[str]:
        try:
            return data['kakao_account']['profile']['nickname']
        except KeyError:
            return

    def get_user_info_with_access_token(self, access_token: str) -> dict:
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        data = requests.get(
            self.request_user_info_path,
            headers=headers
        )
        if data.status_code != 200:
            raise LoginFailedException()
        else:
            data = json.loads(data.text)
            return {
                'id': self.username_prefix + str(data['id']),
                'gender': self._get_gender(data),
                'phone': self._get_phone(data),
                'birth': self._get_birth_day(data),
                'email': self._get_email(data),
                'name': self._get_name(data),
                'nickname': None,
            }


class NaverSocialLoginModule(SocialLoginModule):
    def __init__(self):
        self._request_access_token_path = 'https://nid.naver.com/oauth2.0/token'
        self._request_user_info_path = 'https://openapi.naver.com/v1/nid/me'
        self._client_id = settings.NAVER_API_KEY
        self._secret = settings.NAVER_SECRET_KEY
        self._redirect_uri = settings.NAVER_REDIRECT_URL
        self._username_prefix = 'naver_'

    @property
    def request_access_token_path(self) -> str:
        return self._request_access_token_path

    @property
    def request_user_info_path(self) -> str:
        return self._request_user_info_path

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def secret(self) -> str:
        return self._secret

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    @property
    def username_prefix(self) -> str:
        return self._username_prefix

    @staticmethod
    def _get_birth_day(data_response: dict) -> Optional[datetime]:
        try:
            birth = data_response['birthyear'] + data_response['birthday']
            return datetime.strptime(birth, '%Y%m%d')
        except (KeyError, ValueError):
            return

    @staticmethod
    def _get_gender(data_response: dict) -> Optional[str]:
        return data_response.get('gender')

    @staticmethod
    def _get_phone(data_response: dict) -> Optional[str]:
        try:
            return data_response['phone_number'].replace('-', '').replace(' ', '')
        except KeyError:
            return

    @staticmethod
    def _get_email(data_response: dict) -> Optional[str]:
        return data_response.get('email')

    @staticmethod
    def _get_name(data_response: dict) -> Optional[str]:
        return data_response.get('name')

    def get_user_info_with_access_token(self, access_token: str) -> dict:
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        data = requests.get(
            self.request_user_info_path,
            headers=headers
        )
        if data.status_code != 200:
            raise LoginFailedException()

        data = json.loads(data.text)['response']
        return {
            'id': self.username_prefix + str(data['id']),
            'gender': self._get_gender(data),
            'phone': self._get_phone(data),
            'birth': self._get_birth_day(data),
            'email': self._get_email(data),
            'name': self._get_name(data),
            'nickname': None,
        }


class GoogleSocialLoginModule(SocialLoginModule):
    def __init__(self):
        self._request_access_token_path = 'https://oauth2.googleapis.com/token'
        self._request_user_info_path = 'https://www.googleapis.com/oauth2/v3/userinfo'
        self._client_id = settings.GOOGLE_CLIENT_ID
        self._secret = settings.GOOGLE_SECRET_KEY
        self._redirect_uri = settings.GOOGLE_REDIRECT_URL
        self._username_prefix = 'google_'

    @property
    def request_access_token_path(self) -> str:
        return self._request_access_token_path

    @property
    def request_user_info_path(self) -> str:
        return self._request_user_info_path

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def secret(self) -> str:
        return self._secret

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    @property
    def username_prefix(self) -> str:
        return self._username_prefix

    def get_user_info_with_access_token(self, access_token: str) -> dict:
        data = requests.get(
            self.request_user_info_path,
            params={
                'access_token': access_token
            }
        )
        if data.status_code != 200:
            raise LoginFailedException()

        data = json.loads(data.text)

        return {
            'id': self.username_prefix + str(data.get('sub')),
            'gender': None,
            'phone': None,
            'birth': None,
            'email': None,
            'name': data.get('name'),
            'nickname': None,
        }


class SocialLoginHandler:
    def __init__(self, social_module: SocialLoginModule):
        self.social_module = social_module

    def validate(self, code: str) -> dict:
        access_token = self.social_module.get_access_token_by_code(code)
        return self.social_module.get_user_info_with_access_token(access_token)
