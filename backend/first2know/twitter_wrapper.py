from . import cron
from . import firebase_wrapper
from . import twitter_auth


class Vars:
    _access_token = ""


def update_access_token() -> None:
    client_secret = cron.Vars.client_secret
    encoded_auth = twitter_auth.get_encoded_auth(client_secret)
    refresh_token = firebase_wrapper.get_refresh_token()
    rval = twitter_auth.refresh_access_token(encoded_auth, refresh_token)
    Vars._access_token, new_refresh_token = rval
    firebase_wrapper.write_refresh_token(new_refresh_token)


def tweet(user: str, data: str) -> None:
    print(f"tweeting to {user} {len(data)}")
    media_id = twitter_auth.post_image(Vars._access_token, data)
    message_obj = {
        "text": f"@{user}",
        "media": {
            "media_ids": [media_id]
        },
    }
    resp = twitter_auth.post_tweet(Vars._access_token, message_obj)
    print(resp)
