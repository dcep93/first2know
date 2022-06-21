# https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import base64
import typing

from cryptography.fernet import Fernet

from . import cron


class Vars:
    _app: typing.Any = None  # firebase.FirebaseApplication


def init():
    # pip install git+https://github.com/ozgur/python-firebase
    from firebase import firebase

    Vars._app = firebase.FirebaseApplication(
        'https://first2know-default-rtdb.firebaseio.com/', None)


def get_to_handle() -> typing.List[typing.Dict[str, str]]:
    raw = Vars._app.get("to_handle", None)
    to_handle: typing.Dict[str, typing.Any] = raw  # type: ignore
    return [{"key": i, **j} for i, j in to_handle.items()]


def write_data(key: str, data: str) -> None:
    print("write_data", key)
    Vars._app.patch(f"to_handle/{key}", {"data": data})


def write_refresh_token(refresh_token: str) -> None:
    encrypted = encrypt(refresh_token)
    Vars._app.patch("", {"refresh_token": encrypted})


def get_refresh_token() -> str:
    raw = Vars._app.get("refresh_token", None)
    refresh_token: str = raw  # type: ignore
    return decrypt(refresh_token)


def encrypt(a: str) -> str:
    cipher_suite = _get_cipher_suite()
    b = a.encode('utf-8')
    c = cipher_suite.encrypt(b)
    d = base64.b64encode(c)
    e = d.decode('utf-8')
    return e


def decrypt(e: str) -> str:
    cipher_suite = _get_cipher_suite()
    d = e.encode('utf-8')
    c = base64.b64decode(d)
    b = cipher_suite.decrypt(c)
    a = b.decode('utf-8')
    return a


def _get_cipher_suite() -> Fernet:
    client_secret = cron.Vars.client_secret
    key = base64.b64encode(client_secret.encode('utf-8')[:32])
    return Fernet(key)
