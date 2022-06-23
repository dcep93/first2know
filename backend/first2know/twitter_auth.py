import json
import requests

import urllib.parse
from requests_oauthlib import OAuth1Session

from . import twitter_requester
from . import firebase_wrapper
from . import secrets


def main() -> None:
    _get_refresh_token()
    _get_user_access_token()


def _get_refresh_token() -> None:
    encoded_auth = twitter_requester.get_encoded_auth(
        secrets.Vars.secrets.client_id,
        secrets.Vars.secrets.client_secret,
    )

    scopes = [
        'tweet.read',
        'tweet.write',
        'users.read',
        'offline.access',
    ]
    params = [
        "response_type=code",
        f"client_id={secrets.Vars.secrets.client_id}",
        "redirect_uri=https://first2know.web.app",
        f"scope={'%20'.join(scopes)}",
        "state=state",
        "code_challenge=challenge",
        "code_challenge_method=plain",
    ]
    url = f"https://twitter.com/i/oauth2/authorize?{'&'.join(params)}"
    resp = requests.get(url)
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    print(url)
    auth_code = input("paste code: ")

    resp = requests.post(
        'https://api.twitter.com/2/oauth2/token',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f"Basic {encoded_auth}",
        },
        data={
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://first2know.web.app',
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
            'https://first2know.web.app',
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


if __name__ == "__main__":
    main()
