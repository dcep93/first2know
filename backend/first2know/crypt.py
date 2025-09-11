import base64
import hashlib

from functools import lru_cache

from cryptography.fernet import Fernet  # type: ignore

from . import secrets


@lru_cache
def encrypt(unencrypted_string: str, encryption_key: str) -> str:
    cipher_suite = _get_cipher_suite(encryption_key)
    encoded = unencrypted_string.encode("utf-8")
    encrypted_bytes = cipher_suite.encrypt(encoded)
    encoded_bytes = base64.b64encode(encrypted_bytes)
    encrypted_string = encoded_bytes.decode("utf-8")
    return encrypted_string


@lru_cache
def decrypt(encrypted_string: str, encryption_key: str) -> str:
    cipher_suite = _get_cipher_suite(encryption_key)
    encoded_bytes = encrypted_string.encode("utf-8")
    encrypted_bytes = base64.b64decode(encoded_bytes)
    encoded_string = cipher_suite.decrypt(encrypted_bytes)
    unencrypted_string = encoded_string.decode("utf-8")
    return unencrypted_string


@lru_cache
def get_fernet_key_bytes(encryption_key: str) -> bytes:
    small_key = str_to_md5(secrets.Vars.secrets.email_password + encryption_key)
    big_key = small_key * 32
    fernet_key_bytes = big_key.encode("utf-8")[:32]
    return fernet_key_bytes


@lru_cache
def _get_cipher_suite(encryption_key: str) -> Fernet:
    fernet_key_bytes = get_fernet_key_bytes(encryption_key)
    fernet_key = base64.b64encode(fernet_key_bytes)
    return Fernet(fernet_key)


@lru_cache
def str_to_md5(b: str) -> str:
    return hashlib.md5(b.encode("utf-8")).hexdigest()
