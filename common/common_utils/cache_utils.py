from typing import Any

from django.core.cache import cache
from member.consts import SIGNUP_MACRO_EXPIRE_SECONDS


def generate_dict_value_by_key_to_cache(key: str, value: dict, expire_seconds: int) -> None:
    cache.set(key, value, expire_seconds)


def get_cache_value_by_key(key: str) -> Any:
    return cache.get(key)


def generate_str_value_by_key_to_cache(key: str, value: (str, int), expire_seconds: int) -> None:
    cache.set(key, value, expire_seconds)


def increase_cache_int_value_by_key(key: str) -> int:
    try:
        return cache.incr(key)
    except ValueError:
        generate_str_value_by_key_to_cache(
            key=key,
            value=1,
            expire_seconds=SIGNUP_MACRO_EXPIRE_SECONDS,
        )
        return 1


def delete_cache_value_by_key(key: str) -> None:
    cache.delete(key)
