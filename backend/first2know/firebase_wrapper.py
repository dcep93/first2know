# https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import base64
import json
import threading
import time
import typing

from pydantic import BaseModel

from cryptography.fernet import Fernet

from google.auth import credentials as auth_creds
import firebase_admin
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
    params: typing.Dict[str, typing.Any] = {}
    selector: typing.Optional[str] = None
    evaluate: typing.Optional[str] = None
    evaluation_to_img: typing.Optional[bool] = False
    raw_proxy: typing.Optional[bool] = False
    user_agent_hack: typing.Optional[bool] = False


class User(BaseModel):
    screen_name: str
    user_id: int
    encrypted: str


class ToHandle(BaseModel):
    data_input: DataInput
    data_output: DataOutput
    user: User
    md5: str
    key: str


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
        print("listenF", event.data)
        Vars._raw_all_to_handle = db.reference("/to_handle").get()

    threading.Thread(
        target=lambda: db.reference("/to_handle").listen(listenF),
        daemon=True,
    ).start()


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
    v: typing.Union[str, ToHandle],
) -> typing.Optional[ToHandle]:
    to_handle = v \
        if type(to_handle) is not str \
        else ToHandle(**json.loads(decrypt(to_handle)))
    to_md5 = {"data_input": to_handle.data_inpu}
    return ToHandle(
        key=key,
        **to_handle,
    )
    encrypted_user = data_input_d.pop("user")["encrypted"]
    decrypted_user = decrypt(encrypted_user)
    user = User(**json.loads(decrypted_user))
    if user.encrypted != secrets.Vars.secrets.client_secret:
        return None


def write_data(key: str, data_output: DataOutput) -> None:
    # print("write_data", key, data_output.dict())
    Vars._raw_all_to_handle = None
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
