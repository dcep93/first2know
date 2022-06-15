import base64
import json
import requests
import typing

client_id = "eExSeGFVNHZxbmpzMEo1Wk5qNUc6MTpjaQ"

def main():
    client_secret = input("client_secret: ")
    raw_auth = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(raw_auth.encode('utf-8')).decode('utf-8')

    params = [
        "response_type=code",
        f"client_id={client_id}",
        "redirect_uri=https://first2know.web.app",
        f"scope={'%20'.join(['tweet.read', 'tweet.write', 'users.read', 'offline.access'])}",
        "state=state",
        "code_challenge=challenge",
        "code_challenge_method=plain",
    ]
    url = f"https://twitter.com/i/oauth2/authorize?{'&'.join(params)}"
    print(url)
    auth_code = input("paste code: ")

    resp = requests.post('https://api.twitter.com/2/oauth2/token',
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
    r["encoded_auth"] = encoded_auth
    print(r)

def refresh_access_token(encoded_auth: str, refresh_token: str):
    resp = requests.post('https://api.twitter.com/2/oauth2/token',
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
def read_tweets(access_token: str, tweet_ids: typing.List[str]):
    url = f'https://api.twitter.com/2/tweets?ids={",".join(tweet_ids)}'
    resp = requests.get(
        url,
        headers={
            'Authorization': f"Bearer {access_token}",
        }
    )
    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    r = json.loads(resp.text)
    return r["data"]

def post_tweet(access_token: str, message_obj: typing.Dict[str, str]):
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

if __name__ == "__main__":
    main()
