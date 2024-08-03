from datetime import (
    datetime,
    timedelta,
)

from rest_framework_jwt.settings import api_settings


jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def jwt_payload_handler(guest: 'Guest') -> dict:  # noqa
    payload = {
        'guest_id': guest.pk,
        'member_id': guest.member_id,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA,
    }
    return payload


def get_jwt_login_token(member: 'Member') -> str:  # noqa
    payload = jwt_payload_handler(member.guest)
    token = jwt_encode_handler(payload)
    return token


def get_jwt_refresh_token(guest: 'Guest') -> str:  # noqa
    refresh_expiration = timedelta(days=7)
    refresh_token = jwt_encode_handler({
        'guest_id': guest.id,
        'member_id': guest.member_id,
        'exp': datetime.utcnow() + refresh_expiration
    })
    return refresh_token


def get_jwt_guest_token(guest: 'Guest') -> str:  # noqa
    payload = jwt_payload_handler(guest)
    token = jwt_encode_handler(payload)
    return token
