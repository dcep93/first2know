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
    message_obj = {
        "text": f"@{user}",
        # "media": data,
    }
    resp = twitter_auth.post_tweet(Vars._access_token, message_obj)
    print(resp)


# if __name__ == "__main__":
#     access_token = "MmNtNUZhX25QY3ZsVEZyOGlBMUJFZGpCV1N0Wldvb2pHMVNvdmNlaXJUWlk4OjE2NTU3ODM0NjM5MDQ6MTowOmF0OjE"
#     message_obj = {
#         "text": f"@dcep93",
#         "media": data,
#     }
#     resp = twitter_auth.post_tweet(access_token, message_obj)
#     print(resp)
