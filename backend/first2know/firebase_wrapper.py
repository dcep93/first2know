# https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import base64
import typing

from pydantic import BaseModel

from cryptography.fernet import Fernet

# TODO dcep93 different SDK
# /usr/local/Cellar/python@3.9/3.9.6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/multiprocessing/resource_tracker.py:216: UserWarning: resource_tracker: There appear to be 6 leaked semaphore objects to clean up at shutdown # noqa: E501
# pip install git+https://github.com/ozgur/python-firebase
from firebase import firebase

from . import secrets


class Vars:
    _app: firebase.FirebaseApplication


def init():
    Vars._app = firebase.FirebaseApplication(
        'https://first2know-default-rtdb.firebaseio.com/',
        None,
    )


class ToHandle(BaseModel):
    key: str
    user: str
    url: str
    e_cookie: typing.Optional[str] = None
    params: typing.Optional[typing.Dict[str, typing.Any]] = None
    evaluate: typing.Optional[str] = None
    selector: typing.Optional[str] = None
    data: typing.Optional[str] = None


def get_to_handle() -> typing.List[ToHandle]:
    raw = Vars._app.get("to_handle", None)
    raw_all_to_handle: typing.Dict[str, typing.Any] = raw  # type: ignore
    all_to_handle = [{"key": i, **j} for i, j in raw_all_to_handle.items()]
    return [ToHandle(**i) for i in all_to_handle]


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


# for now, the twitter client secret is also the encryption key
def _get_cipher_suite() -> Fernet:
    client_secret = secrets.Vars.secrets.client_secret
    key = base64.b64encode(client_secret.encode('utf-8')[:32])
    return Fernet(key)
