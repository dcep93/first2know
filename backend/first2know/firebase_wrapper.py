# https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import base64
import json
import threading
import typing

from pydantic import BaseModel

from cryptography.fernet import Fernet

import firebase_admin
from google.auth import credentials as auth_creds
from firebase_admin import credentials as firebase_creds
from firebase_admin import db

from . import secrets


class ErrorType(BaseModel):
    version: str
    time: float
    message: str


class ScreenshotData(BaseModel):
    img_url: str
    md5: str
    evaluation: typing.Any


class DataOutput(BaseModel):
    times: typing.List[float]
    screenshot_data: typing.Optional[ScreenshotData] = None
    error: typing.Optional[ErrorType] = None


class DataInput(BaseModel):
    url: str
    params: typing.Optional[typing.Dict[str, typing.Any]]
    selector: typing.Optional[str]
    evaluate: typing.Optional[str]
    evaluation_to_img: typing.Optional[bool]


class User(BaseModel):
    screen_name: str
    user_id: int
    encrypted: str


class ToHandle(BaseModel):
    data_input: DataInput
    data_output: DataOutput
    user: User
    key: str


class Vars:
    _raw_all_to_handle: typing.Optional[typing.Dict[str,
                                                    typing.Dict[str,
                                                                typing.Any]]]


class Creds(firebase_creds.ApplicationDefault):
    def get_credential(self):
        return auth_creds.AnonymousCredentials()


project = 'first2know'


def init():
    creds = Creds()
    firebase_admin.initialize_app(
        creds,
        options={
            'databaseURL': f'https://{project}-default-rtdb.firebaseio.com/',
            'projectId': project,
        },
    )

    def listenF(event: db.Event):
        Vars._raw_all_to_handle = event.data

    threading.Thread(
        target=lambda: db.reference("/to_handle").listen(listenF),
        daemon=True,
    ).start()


def get_to_handle() -> typing.List[ToHandle]:
    if Vars._raw_all_to_handle is None:
        return []
    return [
        i for i in [
            _decrypt_to_handle(k, v["encrypted"], v["data_output"])
            for k, v in Vars._raw_all_to_handle.items()
        ] if i
    ]


def _decrypt_to_handle(
    key: str,
    encrypted: str,
    data_output: DataOutput,
) -> typing.Optional[ToHandle]:
    data_input_d = json.loads(decrypt(encrypted))
    encrypted_user = data_input_d.pop("user")["encrypted"]
    user = User(**json.loads(decrypt(encrypted_user)))
    if user.encrypted != secrets.Vars.secrets.client_secret:
        return None
    to_handle = ToHandle(
        key=key,
        user=user,
        data_output=data_output,
        data_input=DataInput(**data_input_d),
    )
    return to_handle


def write_data(key: str, data_output: DataOutput) -> None:
    # print("write_data", key)
    db.reference(f"to_handle/{key}/data_output").set(data_output.dict())


def write_token(token: str) -> None:
    encrypted = encrypt(token)
    db.reference("token").set(encrypted)


def get_token() -> str:
    raw = db.reference("token").get()
    token: str = raw  # type: ignore
    return decrypt(token)


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
