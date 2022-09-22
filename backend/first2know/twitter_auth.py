from requests_oauthlib import OAuth1Session  # type: ignore

from urllib.parse import parse_qs

from . import secrets


def login_request_token():
    oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        client_secret=secrets.Vars.secrets.api_key_secret,
    )
    resp = oauth.post('https://api.twitter.com/oauth/request_token')
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    resp_json = parse_qs(resp.text)
    return {
        "oauth_token": resp_json["oauth_token"][0],
    }


def login_access_token(oauth_token: str, oauth_verifier: str):
    oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        client_secret=secrets.Vars.secrets.api_key_secret,
    )
    resp = oauth.post(
        'https://api.twitter.com/oauth/access_token',
        data={
            "oauth_verifier": oauth_verifier,
            "oauth_token": oauth_token,
        },
    )
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    resp_json = parse_qs(resp.text)
    return {
        "screen_name": resp_json["screen_name"][0],
        "user_id": resp_json["user_id"][0],
    }
