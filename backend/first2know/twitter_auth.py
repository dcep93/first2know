import base64
import json
import requests
import typing

from . import firebase_wrapper

client_id = "eExSeGFVNHZxbmpzMEo1Wk5qNUc6MTpjaQ"


def main() -> None:
    client_secret = input("client_secret: ")
    encoded_auth = get_encoded_auth(client_secret)

    scopes = ['tweet.read', 'tweet.write', 'users.read', 'offline.access']
    params = [
        "response_type=code",
        f"client_id={client_id}",
        "redirect_uri=https://first2know.web.app",
        f"scope={'%20'.join(scopes)}",
        "state=state",
        "code_challenge=challenge",
        "code_challenge_method=plain",
    ]
    url = f"https://twitter.com/i/oauth2/authorize?{'&'.join(params)}"
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
    encrypted_refresh_token = firebase_wrapper.encrypt(r["refresh_token"])
    print(r)
    print("place encrypted_refresh_token in firebase")
    print(encrypted_refresh_token)


def get_encoded_auth(client_secret: str) -> str:
    raw_auth = f"{client_id}:{client_secret}"
    return base64.b64encode(raw_auth.encode('utf-8')).decode('utf-8')


def refresh_access_token(
    encoded_auth: str,
    refresh_token: str,
) -> typing.Tuple[str, str]:
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


# tweet_ids = ['1261326399320715264', '1278347468690915330']
def read_tweets(access_token: str, tweet_ids: typing.List[str]) -> typing.Any:
    url = f'https://api.twitter.com/2/tweets?ids={",".join(tweet_ids)}'
    resp = requests.get(url,
                        headers={
                            'Authorization': f"Bearer {access_token}",
                        })
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    return r["data"]


def post_tweet(
    access_token: str,
    message_obj: typing.Dict[str, str],
) -> typing.Any:
    resp = requests.post(
        'https://api.twitter.com/2/tweets',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {access_token}",
        },
        data=json.dumps(message_obj),
    )
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    return r["data"]


def post_image(access_token: str, data: str) -> int:
    message_obj = {"media_data": data, "media_category": "tweet_image"}
    resp = requests.post(
        'https://api.twitter.com/2/tweets',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {access_token}",
        },
        data=json.dumps(message_obj),
    )
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    return r["media_id"]


if __name__ == "__main__":
    main()
