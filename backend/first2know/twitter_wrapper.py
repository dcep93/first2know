from . import twitter_requester


class Vars:
    _access_token: str


def refresh_access_token(refresh_token: str) -> str:
    rval = twitter_requester.refresh_access_token(refresh_token)
    Vars._access_token, new_refresh_token = rval
    return new_refresh_token


def tweet(user: str, img_data: str) -> None:
    # TODO dcep93 restore
    return
    if Vars._access_token is None:
        raise Exception("need to refresh_access_token")
    print(f"tweeting to {user} {len(img_data)}")
    media_id = twitter_requester.post_image(img_data)
    message_obj = {
        "text": f"@{user}",
        "media": {
            "media_ids": [str(media_id)]
        },
    }
    resp = twitter_requester.post_tweet(Vars._access_token, message_obj)
    print(resp)
