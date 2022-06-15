# pip install git+https://github.com/ozgur/python-firebase
from firebase import firebase

# for now, this is both the twitter client secret and the encryption key
client_secret = "Z7EFPX2T6Fi8KEtvWsneFGdymDBWwjSOH_m4yNPGd1RQIjRTji"

class Vars:
    app: firebase.FirebaseApplication = None # type: ignore


def init():
    Vars.app = firebase.FirebaseApplication('https://first2know-default-rtdb.firebaseio.com/', None)

 
def get_to_handle():
    return [
        {"key": "a", "user": "dcep93", "url": "https://chess.com", "img_data": "", "fetch_params": {}, "css_selector": None},
        {"key": "b", "user": "dcep93", "url": "https://www.chess.com/member/dcep93", "img_data": "", "fetch_params": {}, "css_selector": None},
    ]

def write_img_data(key: str, img_data: bytes):
    print("write_img_data", key)

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
