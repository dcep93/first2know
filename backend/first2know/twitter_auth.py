import json
import requests

import urllib.parse
from requests_oauthlib import OAuth1Session

from . import twitter_wrapper
from . import firebase_wrapper
from . import secrets


def get_authorize_url() -> str:
    scopes = [
        'tweet.read',
        'tweet.write',
        'users.read',
        'offline.access',
    ]
    params = [
        "response_type=code",
        f"client_id={secrets.Vars.secrets.client_id}",
        f"redirect_uri={secrets.Vars.secrets.redirect_uri}",
        f"scope={'%20'.join(scopes)}",
        "state=state",
        "code_challenge=challenge",
        "code_challenge_method=plain",
    ]
    url = f"https://twitter.com/i/oauth2/authorize?{'&'.join(params)}"
    return url


def _get_refresh_token() -> None:
    url = get_authorize_url()
    resp = requests.get(url)
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    print(url)
    auth_code = input("paste code: ")

    encoded_auth = twitter_wrapper.get_encoded_auth(
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
            'grant_type': 'authorization_code',
            'redirect_uri': secrets.Vars.secrets.redirect_uri,
            'code_verifier': 'challenge',
            'code': auth_code,
        },
    )
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    print(r)
    refresh_token = r["refresh_token"]
    firebase_wrapper.init()
    firebase_wrapper.write_refresh_token(refresh_token)
    print("updated firebase")


def _get_user_access_token() -> None:
    params = {
        "oauth_callback":
        urllib.parse.quote(
            secrets.Vars.secrets.redirect_uri,
            safe='',
        ),
        "x_auth_access_type":
        "write",
    }
    request_token_url = "https://api.twitter.com/oauth/request_token?" + \
        "&".join([f"{i}={j}" for i, j in params.items()])
    oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        client_secret=secrets.Vars.secrets.api_key_secret,
    )
    fetch_response = oauth.fetch_request_token(request_token_url)
    oauth_token = fetch_response["oauth_token"]
    url = "https://api.twitter.com/oauth/authorize?" \
        + f"oauth_token={oauth_token}"
    resp = requests.get(url)
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    print(url)
    oauth_verifier = input("paste oauth_verifier: ")
    resp = requests.post(
        'https://api.twitter.com/oauth/access_token',
        data={
            "oauth_verifier": oauth_verifier,
            "oauth_token": oauth_token,
        },
    )
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    print(resp.text)


def login_request_token():
    oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        client_secret=secrets.Vars.secrets.api_key_secret,
    )
    resp = oauth.post('https://api.twitter.com/oauth/request_token')
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    return resp.text


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
    return resp.text
