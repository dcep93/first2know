from . import secrets
from . import twitter_auth


class Vars:
    _access_token: str


def refresh_access_token(refresh_token: str) -> str:
    encoded_auth = twitter_auth.get_encoded_auth(
        secrets.Vars.secrets.client_id,
        secrets.Vars.secrets.client_secret,
    )
    rval = twitter_auth.refresh_access_token(encoded_auth, refresh_token)
    Vars._access_token, new_refresh_token = rval
    return new_refresh_token


def tweet(user: str, data: str) -> None:
    if Vars._access_token is None:
        raise Exception("need to refresh_access_token")
    print(f"tweeting to {user} {len(data)}")
    media_id = twitter_auth.post_image(data)
    message_obj = {
        "text": f"@{user}",
        "media": {
            "media_ids": [media_id]
        },
    }
    resp = twitter_auth.post_tweet(Vars._access_token, message_obj)
    print(resp)
