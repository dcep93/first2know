import json
import typing

from requests_oauthlib import OAuth1Session

from . import secrets


def message(user_id: int, img_data: str):
    media_id = _post_image(img_data)
    return _send_message(user_id, "", media_id)


def tweet(text: str, img_data: str) -> str:
    media_id = _post_image(img_data)
    tweet_id = _post_tweet(text, media_id)
    resp = _read_tweets(
        [tweet_id], {
            "expansions": "attachments.media_keys",
            "media.fields": "url,preview_image_url",
        })
    return resp["includes"]["media"][0]["url"]


def _read_tweets(
    tweet_ids: typing.List[int],
    params: typing.Optional[typing.Dict[str, str]] = None,
) -> typing.Any:
    params = dict(params) if params else {}
    params["ids"] = ",".join([str(i) for i in tweet_ids])
    params_arr = [f"{k}={v}" for k, v in params.items()]
    url = f'https://api.twitter.com/2/tweets?{"&".join(params_arr)}'
    oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        secrets.Vars.secrets.api_key_secret,
        secrets.Vars.secrets.oauth_token,
        secrets.Vars.secrets.oauth_token_secret,
    )
    resp = oauth.get(url)
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    return json.loads(resp.text)


def _post_image(img_data: str) -> int:
    oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        secrets.Vars.secrets.api_key_secret,
        secrets.Vars.secrets.oauth_token,
        secrets.Vars.secrets.oauth_token_secret,
    )
    resp = oauth.post(
        'https://upload.twitter.com/1.1/media/upload.json',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={"media_data": img_data},
    )
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    return r["media_id"]


def _post_tweet(text: str, media_id: int) -> int:
    message_obj = {
        "text": text,
        "media": {
            "media_ids": [str(media_id)]
        },
    }
    oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        secrets.Vars.secrets.api_key_secret,
        secrets.Vars.secrets.oauth_token,
        secrets.Vars.secrets.oauth_token_secret,
    )
    resp = oauth.post(
        'https://api.twitter.com/2/tweets',
        headers={
            'Content-Type': 'application/json',
        },
        data=json.dumps(message_obj),
    )
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    return r["data"]["id"]


def _send_message(user_id: int, text: str, media_id: int):
    message_obj = {
        "event": {
            "type": "message_create",
            "message_create": {
                "target": {
                    "recipient_id": user_id
                },
                "message_data": {
                    "text": text,
                    "attachment": {
                        "type": "media",
                        "media": {
                            "id": media_id
                        }
                    }
                }
            }
        }
    }

    oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        secrets.Vars.secrets.api_key_secret,
        secrets.Vars.secrets.oauth_token,
        secrets.Vars.secrets.oauth_token_secret,
    )

    resp = oauth.post(
        'https://api.twitter.com/1.1/direct_messages/events/new.json',
        headers={
            'Content-Type': 'application/json',
        },
        data=json.dumps(message_obj),
    )

    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    return r["data"]
