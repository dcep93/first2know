import time

import firebase_wrapper
import twitter_auth

class Vars:
    access_token = ""

def update_access_token(encoded_auth: str, refresh_token: str):
    Vars.access_token, new_refresh_token = twitter_auth.refresh_access_token(encoded_auth, refresh_token)
    firebase_wrapper.write_refresh_token(new_refresh_token)

def tweet(user: str, img_data: bytes):
    print(f"tweeting to {user} {len(img_data)}")
    message_obj = {"text": f"@{user} {len(img_data)} {time.time()}"}
    resp = twitter_auth.post_tweet(Vars.access_token, message_obj)
    print(resp)
