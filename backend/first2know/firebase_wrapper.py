# https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import json
import threading
import time
import typing

from pydantic import BaseModel  # type: ignore

from google.auth import credentials as auth_creds  # type: ignore
import firebase_admin  # type: ignore
from firebase_admin import credentials as firebase_creds  # type: ignore
from firebase_admin import db  # type: ignore

from . import crypt
from . import logger


class ErrorType(BaseModel):
    version: str
    time: float
    message: str


class ScreenshotData(BaseModel):
    md5: str
    evaluation: typing.Optional[str] = None


class DataOutput(BaseModel):
    screenshot_data: typing.Optional[ScreenshotData] = None
    time: typing.Optional[float] = None
    error: typing.Optional[ErrorType] = None


class DataInput(BaseModel):
    url: typing.Optional[str] = None
    params: typing.Optional[typing.Dict[str, typing.Any]] = None
    selector: typing.Optional[str] = None
    evaluate: typing.Optional[str] = None
    evaluation_to_img: typing.Optional[bool] = False
    user_agent_hack: typing.Optional[bool] = None
    raw_proxy: typing.Optional[bool] = None


class ToHandle(BaseModel):
    data_input: DataInput
    user: str
    key: typing.Optional[str]
    data_output: typing.Optional[DataOutput] = None


class Vars:
    _raw_all_to_handle: typing.Optional[typing.Dict[str, typing.Dict[str, str]]] = None


class Creds(firebase_creds.ApplicationDefault):

    def get_credential(self) -> auth_creds.AnonymousCredentials:
        return auth_creds.AnonymousCredentials()


project = "first2know"


def init() -> None:
    creds = Creds()
    firebase_admin.initialize_app(
        creds,
        options={
            "databaseURL": f"https://{project}-default-rtdb.firebaseio.com/",
            "projectId": project,
        },
    )

    def listenF(event: db.Event) -> None:
        if Vars._raw_all_to_handle is None:
            logger.log("firebase_wrapper.init.listenF")
            Vars._raw_all_to_handle = event.data
            return
        Vars._raw_all_to_handle = db.reference("/to_handle").get()

    threading.Thread(
        target=lambda: db.reference("/to_handle").listen(listenF),
        daemon=True,
    ).start()
    logger.log("firebase_wrapper.init.initialized")


def wait_10s_for_data() -> None:
    now = time.time()
    while time.time() - now <= 10:
        if Vars._raw_all_to_handle is not None:
            return
        time.sleep(0.001)


def get_to_handle() -> typing.List[ToHandle]:
    if Vars._raw_all_to_handle is None:
        return []
    return [_extract_to_handle(k, v) for k, v in Vars._raw_all_to_handle.items()]


def _extract_to_handle(
    key: str,
    d: typing.Dict[str, str],
) -> ToHandle:
    decrypted = crypt.decrypt(d["encrypted"], d["user"])
    loaded = json.loads(decrypted)
    loaded["key"] = key
    return ToHandle.parse_obj(loaded)


def write_data(to_handle: ToHandle) -> None:
    d = to_handle.dict()
    dd = {k: v for k, v in d.items() if v}
    ddd = json.dumps(dd)
    encrypted = crypt.encrypt(ddd, to_handle.user)
    db.reference(f"to_handle/{to_handle.key}").set(
        {"encrypted": encrypted, "user": to_handle.user}
    )


def write_token(token: str) -> None:
    ref = db.reference("token")

    def f() -> None:
        ref.set(token)

    for _ in range(3):
        try:
            f()
            return
        except:
            logger.log("firebase_wrapper.write_token.fail")
            pass
    f()


def get_token() -> str:
    raw = db.reference("token").get()
    token: str = raw  # type: ignore
    return token
