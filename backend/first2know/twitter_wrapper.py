import time

import firebase_wrapper
import twitter_auth

class Vars:
    access_token = ""

def update_access_token():
    encoded_auth = twitter_auth.get_encoded_auth(firebase_wrapper.client_secret)
    refresh_token = firebase_wrapper.get_refresh_token()
    rval = twitter_auth.refresh_access_token(encoded_auth, refresh_token)
    Vars.access_token, new_refresh_token = rval
    firebase_wrapper.write_refresh_token(new_refresh_token)

def tweet(user: str, img_data: bytes):
    print(f"tweeting to {user} {len(img_data)}")
    message_obj = {"text": f"@{user} {len(img_data)} {time.time()}"}
    resp = twitter_auth.post_tweet(Vars.access_token, message_obj)
    print(resp)
