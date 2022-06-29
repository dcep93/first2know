# https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import base64
import json
import typing

from pydantic import BaseModel

from cryptography.fernet import Fernet

import firebase_admin
from firebase_admin import db

from . import secrets


class ErrorType(BaseModel):
    version: str
    time: float
    message: str


class DataOutputType(BaseModel):
    img_data: typing.Optional[str]
    evaluation: typing.Optional[typing.Any]
    times: typing.List[float]
    error: typing.Optional[ErrorType] = None


class ScreenshotPayload(BaseModel):
    url: str
    params: typing.Optional[typing.Dict[str, typing.Any]]
    selector: typing.Optional[str]
    evaluate: typing.Optional[str]
    evaluation_to_img: bool
    no_tweet: bool = False


class ToHandle(BaseModel):
    data_input: ScreenshotPayload
    data_output: DataOutputType
    user_name: str
    key: str


class Vars:
    _raw_all_to_handle: typing.Dict[str, typing.Dict[str, typing.Any]] = {}


project = 'first2know'


def init():
    firebase_admin.initialize_app(options={
        'databaseURL':
        'https://{project}-default-rtdb.firebaseio.com/'
    }, )

    def listenF(raw):
        Vars._raw_all_to_handle = raw

    db.reference("/to_handle").listen(listenF)


def get_to_handle() -> typing.List[ToHandle]:
    return [
        i for i in [
            _decrypt_to_handle(k, v["encrypted"], v["data_output"])
            for k, v in Vars._raw_all_to_handle.items()
        ] if i
    ]


def _decrypt_to_handle(
    key: str,
    encrypted: str,
    data_output: DataOutputType,
) -> typing.Optional[ToHandle]:
    data_input = json.loads(decrypt(encrypted))
    encrypted_user = data_input.pop("user")["encrypted"]
    user = json.loads(decrypt(encrypted_user))
    if user["client_secret"] != secrets.Vars.secrets.client_secret:
        return None
    user_name = user["screen_name"]
    to_handle = ToHandle(
        key=key,
        user_name=user_name,
        data_output=data_output,
        data_input=data_input,
    )
    return to_handle


def write_data(key: str, data_output: DataOutputType) -> None:
    # print("write_data", key)
    db.reference(f"to_handle/{key}/data_output").set(data_output.dict())


def write_refresh_token(refresh_token: str) -> None:
    encrypted = encrypt(refresh_token)
    db.reference("refresh_token").set(encrypted)


def get_refresh_token() -> str:
    raw = db.reference("refresh_token").get()
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
