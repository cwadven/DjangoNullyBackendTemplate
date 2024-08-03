import jwt
from django.apps import apps
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.utils.encoding import smart_str
from django.utils.translation import gettext as _
from member.exceptions import BlackMemberException
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication,
    get_authorization_header,
)
from rest_framework.exceptions import APIException
from rest_framework_jwt.settings import api_settings

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class DefaultAuthentication(BaseAuthentication):
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        jwt_value = self.get_jwt_value(request)

        if jwt_value is None:
            return None, None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('만료된 토큰입니다.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('잘못된 토큰 형식입니다.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            msg = _('유효하지 않은 토큰 입니다.')
            raise exceptions.AuthenticationFailed(msg)

        guest = self.authenticate_credentials(payload)
        request.guest = guest
        if guest.is_blacklisted:
            raise BlackMemberException()
        if guest.member:
            request.member = guest.member
            guest.member.raise_if_inaccessible()
        return guest, jwt_value

    def enforce_csrf(self, request):
        return

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if smart_str(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format(api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)

    def authenticate_credentials(self, payload):
        Guest = apps.get_model('member', 'Guest')
        guest_id = payload.get('guest_id')

        if not guest_id:
            msg = _('잘못된 Token 입니다.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            guest = Guest.objects.select_related('member').get(id=guest_id)
        except Guest.DoesNotExist:
            msg = _('존재하지 않는 사용자입니다.')
            raise exceptions.AuthenticationFailed(msg)

        return guest


class JWTAuthenticationMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        try:
            DefaultAuthentication().authenticate(request)
        except APIException:
            pass
