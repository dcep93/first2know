import typing

# TODO dcep93
# pip install git+https://github.com/ozgur/python-firebase
from firebase import firebase

# for now, this is both the twitter client secret and the encryption key
# TODO dcep93
client_secret = "Z7EFPX2T6Fi8KEtvWsneFGdymDBWwjSOH_m4yNPGd1RQIjRTji"

class Vars:
    app: firebase.FirebaseApplication = None # type: ignore


def init():
    Vars.app = firebase.FirebaseApplication('https://first2know-default-rtdb.firebaseio.com/', None)

 
def get_to_handle():
    raw = Vars.app.get("to_handle", None)
    to_handle: typing.Dict[str, typing.Any] = raw # type: ignore
    return to_handle.values()

def write_img_data(key: str, img_data: str):
    print("write_img_data", key)
    Vars.app.patch(f"to_handle/{key}", {"img_data": img_data})

def write_refresh_token(refresh_token: str):
    print("write_refresh_token", refresh_token)
    encrypted = encrypt(refresh_token)
    Vars.app.patch("", {"refresh_token": encrypted})

def get_refresh_token() -> str:
    raw = Vars.app.get("refresh_token", None)
    refresh_token: str = raw # type: ignore
    return decrypt(refresh_token)

def encrypt(s: str) -> str:
    return s

def decrypt(s: str) -> str:
    return s
