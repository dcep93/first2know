import base64
import json
import requests
import typing

from requests_oauthlib import OAuth1Session

from . import secrets


def get_encoded_auth(client_id: str, client_secret: str) -> str:
    raw_auth = f"{client_id}:{client_secret}"
    return base64.b64encode(raw_auth.encode('utf-8')).decode('utf-8')


def refresh_access_token(refresh_token: str) -> typing.Tuple[str, str]:
    encoded_auth = get_encoded_auth(
        secrets.Vars.secrets.client_id,
        secrets.Vars.secrets.client_secret,
    )
    resp = requests.post(
        'https://api.twitter.com/2/oauth2/token',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f"Basic {encoded_auth}",
        },
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        },
    )
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    return r["access_token"], r["refresh_token"]


# tweet_ids = [1261326399320715264, 1278347468690915330]
def read_tweets(access_token: str, tweet_ids: typing.List[int]) -> typing.Any:
    str_ids = ",".join([str(i) for i in tweet_ids])
    url = f'https://api.twitter.com/2/tweets?ids={str_ids}'
    resp = requests.get(url,
                        headers={
                            'Authorization': f"Bearer {access_token}",
                        })
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    return r["data"]


def post_tweet(message_obj: typing.Dict[str, str], ) -> typing.Any:
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
    return r["data"]


def post_image(data: str) -> int:
    oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        secrets.Vars.secrets.api_key_secret,
        secrets.Vars.secrets.oauth_token,
        secrets.Vars.secrets.oauth_token_secret,
    )
    message_obj = {"media_data": data}
    resp = oauth.post(
        'https://upload.twitter.com/1.1/media/upload.json',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data=message_obj,
    )
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    return r["media_id"]
