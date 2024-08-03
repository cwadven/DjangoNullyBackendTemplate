import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings


fernet = Fernet(
    base64.urlsafe_b64encode(
        hashlib.sha256(
            settings.SECRET_KEY.encode()
        ).digest()
    )
)


def encrypt_integer(integer: int) -> str:
    integer_bytes = str(integer).encode()
    encrypted = fernet.encrypt(integer_bytes)
    return encrypted.decode()


def decrypt_integer(encrypted: str) -> int:
    decrypted_bytes = fernet.decrypt(encrypted)
    decrypted_integer = int(decrypted_bytes.decode())
    return decrypted_integer
