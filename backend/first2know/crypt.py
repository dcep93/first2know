import base64
import hashlib

from cryptography.fernet import Fernet  # type: ignore

from . import secrets


def encrypt(unencrypted_string: str, encryption_key: str) -> str:
    cipher_suite = _get_cipher_suite(encryption_key)
    encoded = unencrypted_string.encode("utf-8")
    encrypted_bytes = cipher_suite.encrypt(encoded)
    encoded_string = base64.b64encode(encrypted_bytes)
    encrypted_string = encoded_string.decode("utf-8")
    return encrypted_string


def decrypt(encrypted_string: str, encryption_key: str) -> str:
    cipher_suite = _get_cipher_suite(encryption_key)
    encoded_string = encrypted_string.encode("utf-8")
    encrypted_bytes = base64.b64decode(encoded_string)
    encoded_string = cipher_suite.decrypt(encrypted_bytes)
    unencrypted_string = encoded_string.decode("utf-8")
    return unencrypted_string


# for now, the email password is also the encryption key
def _get_cipher_suite(encryption_key: str) -> Fernet:
    small_key = str_to_md5(secrets.Vars.secrets.email_password + encryption_key)
    raw_key = small_key * 32
    key = base64.b64encode(raw_key.encode("utf-8")[:32])
    return Fernet(key)


def str_to_md5(b: str) -> str:
    return hashlib.md5(b.encode("utf-8")).hexdigest()
