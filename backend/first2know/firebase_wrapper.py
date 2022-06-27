# https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import base64
import json
import typing

from pydantic import BaseModel

from cryptography.fernet import Fernet

# /usr/local/Cellar/python@3.9/3.9.6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/multiprocessing/resource_tracker.py:216: UserWarning: resource_tracker: There appear to be 6 leaked semaphore objects to clean up at shutdown # noqa: E501
# pip install git+https://github.com/ozgur/python-firebase
from firebase import firebase

from . import secrets


class DataType(BaseModel):
    img_data: str
    evaluation: typing.Optional[str]
    times: typing.List[float]


class ToHandle(BaseModel):
    url: str
    params: typing.Optional[typing.Dict[str, typing.Any]]
    evaluate: typing.Optional[str]
    selector: typing.Optional[str]
    evaluation_to_img: bool

    user_name: str

    data: DataType
    key: str


class Vars:
    _app: firebase.FirebaseApplication


def init():
    Vars._app = firebase.FirebaseApplication(
        'https://first2know-default-rtdb.firebaseio.com/',
        None,
    )


def get_to_handle() -> typing.List[ToHandle]:
    raw = Vars._app.get("to_handle", None)
    raw_all_to_handle: typing.Dict = raw  # type: ignore
    return [
        i for i in [
            _decrypt_to_handle(k, v["encrypted"], v.get("data"))
            for k, v in raw_all_to_handle.items()
        ] if i
    ]


def _decrypt_to_handle(
        key: str, encrypted: str,
        data: typing.Optional[DataType]) -> typing.Optional[ToHandle]:
    loaded = json.loads(decrypt(encrypted))
    encrypted_user = loaded.pop("user")["encrypted"]
    user = json.loads(decrypt(encrypted_user))
    if user["client_secret"] != secrets.Vars.secrets.client_secret:
        return None
    asserted_data = DataType(
        img_data="",
        evaluation=None,
        times=[],
    ) if data is None else data
    to_handle = ToHandle(
        key=key,
        user_name=user["screen_name"],
        data=asserted_data,
        **loaded,
    )
    return to_handle


def write_data(key: str, data: DataType) -> None:
    # print("write_data", key)
    Vars._app.patch(f"to_handle/{key}/data", data.dict())


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
