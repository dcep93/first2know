# https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import base64
import hashlib
import json
import threading
import time
import typing

from pydantic import BaseModel

from cryptography.fernet import Fernet

from google.auth import credentials as auth_creds  # type: ignore
import firebase_admin  # type: ignore
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
    evaluation: typing.Optional[str] = None


class DataOutput(BaseModel):
    screenshot_data: typing.Optional[ScreenshotData] = None
    time: typing.Optional[float] = None
    error: typing.Optional[ErrorType] = None


class DataInput(BaseModel):
    url: str
    params: typing.Dict[str, typing.Any] = {}
    selector: typing.Optional[str] = None
    evaluate: typing.Optional[str] = None
    evaluation_to_img: typing.Optional[bool] = False
    user_agent_hack: typing.Optional[bool] = None
    raw_proxy: typing.Optional[bool] = None


class User(BaseModel):
    screen_name: str
    user_id: int
    encrypted: str


class ToHandle(BaseModel):
    data_input: DataInput
    user: User
    md5: str
    key: str
    data_output: typing.Optional[DataOutput] = None


class Vars:
    _raw_all_to_handle: typing.Optional[typing.Dict[str, typing.Dict[
        str, typing.Any]]] = None


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
        if Vars._raw_all_to_handle is None:
            print("init listenF")
            Vars._raw_all_to_handle = event.data
            return
        Vars._raw_all_to_handle = db.reference("/to_handle").get()

    threading.Thread(
        target=lambda: db.reference("/to_handle").listen(listenF),
        daemon=True,
    ).start()
    print("firebase initialized")


def wait_10s_for_data():
    now = time.time()
    while time.time() - now <= 10:
        if Vars._raw_all_to_handle is not None:
            return
        time.sleep(0.001)


def get_to_handle() -> typing.List[ToHandle]:
    if Vars._raw_all_to_handle is None:
        return []
    return [
        i for i in
        [_extract_to_handle(k, v) for k, v in Vars._raw_all_to_handle.items()]
        if i
    ]


def _extract_to_handle(
    key: str,
    d: typing.Dict[str, typing.Any],
) -> typing.Optional[ToHandle]:
    d = dict(d)
    encrypted = d.pop("encrypted", None)

    if encrypted:
        decrypted = decrypt(encrypted)
        d["data_input"] = json.loads(decrypted)

    to_handle = ToHandle(
        key=key,
        **d,
    )

    encrypted_user = decrypt(to_handle.user.encrypted)

    decrypted_user = decrypt(encrypted_user)
    user = User(**json.loads(decrypted_user))

    if user.encrypted != secrets.Vars.secrets.client_secret:
        print("bad_encryption")
        return None

    to_md5 = json.dumps(
        [
            dict(to_handle.data_input),
            encrypted_user,
        ],
        separators=(',', ':'),
    )
    if str_to_md5(to_md5) != to_handle.md5:
        print(user)
        print(to_handle.user)
        print("bad_md5", key)
        return None

    return to_handle


def str_to_md5(b: str) -> str:
    return hashlib.md5(b.encode('utf-8')).hexdigest()


def write_data(key: str, data_output: DataOutput) -> None:
    db.reference(f"to_handle/{key}/data_output").set(data_output.dict())


def write_token(token: str) -> None:
    encrypted = encrypt(token)
    ref = db.reference("token")
    def f(): return ref.set(encrypted)
    for _ in range(3):
        try:
            f()
            return
        except:
            print("failed to write token")
            pass
    f()


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
