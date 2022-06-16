import base64
import typing

# TODO dcep93 - install in container
from cryptography.fernet import Fernet

import cron

# TODO dcep93 - install in container
# pip install git+https://github.com/ozgur/python-firebase
from firebase import firebase

class Vars:
    _app: firebase.FirebaseApplication = None # type: ignore


def init():
    Vars._app = firebase.FirebaseApplication('https://first2know-default-rtdb.firebaseio.com/', None)

 
def get_to_handle():
    raw = Vars._app.get("to_handle", None)
    to_handle: typing.Dict[str, typing.Any] = raw # type: ignore
    return to_handle.values()

def write_img_data(key: str, img_data: str):
    print("write_img_data", key)
    Vars._app.patch(f"to_handle/{key}", {"img_data": img_data})

def write_refresh_token(refresh_token: str):
    print("write_refresh_token", refresh_token)
    encrypted = encrypt(refresh_token)
    Vars._app.patch("", {"refresh_token": encrypted})

def get_refresh_token() -> str:
    raw = Vars._app.get("refresh_token", None)
    refresh_token: str = raw # type: ignore
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

def _get_cipher_suite():
    client_secret = cron.Vars.client_secret
    key = base64.b64encode(client_secret.encode('utf-8')[:32])
    return Fernet(key)
