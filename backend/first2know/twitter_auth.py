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
    print("login_request_token", resp_json)
    return {
        "oauth_token": resp_json["oauth_token"],
    }


def login_access_token(oauth_token: str, oauth_verifier: str):
    oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        client_secret=secrets.Vars.secrets.api_key_secret,
    )
    print("login_access_token", oauth_token, oauth_verifier)
    resp = oauth.post(
        'https://api.twitter.com/oauth/access_token',
        data={
            "oauth_verifier": oauth_verifier,
            "oauth_token": oauth_token,
        },
    )
    #       File "/usr/local/lib/python3.9/dist-packages/anyio/_backends/_asyncio.py", line 807, in run
    #     result = context.run(func, *args)
    #   File "/root/first2know/server.py", line 140, in post_twitter_access_token
    #     resp_json = twitter_auth.login_access_token(
    #   File "/root/first2know/twitter_auth.py", line 37, in login_access_token
    #     raise Exception(resp.text)
    # Exception: Request token missing

    if resp.status_code >= 300:
        print(resp)
        raise Exception(resp.text)
    resp_json = parse_qs(resp.text)
    return {
        "screen_name": resp_json["screen_name"][0],
        "user_id": resp_json["user_id"][0],
    }


# https://requests-oauthlib.readthedocs.io/en/v1.3.1/oauth1_workflow.html
def get_oauth_tokens():
    request_oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        secrets.Vars.secrets.api_key_secret,
    )
    request_token = request_oauth.fetch_request_token(
        "https://api.twitter.com/oauth/request_token")
    authorization_url = request_oauth.authorization_url(
        "https://api.twitter.com/oauth/authorize")
    redirect_response = input(f"{authorization_url}\n")
    verifier = request_oauth.parse_authorization_response(
        redirect_response)["oauth_verifier"]
    access_oauth = OAuth1Session(
        secrets.Vars.secrets.api_key,
        secrets.Vars.secrets.api_key_secret,
        resource_owner_key=request_token["oauth_token"],
        resource_owner_secret=request_token["oauth_token_secret"],
        verifier=verifier,
    )
    oauth_tokens = access_oauth.fetch_access_token(
        "https://api.twitter.com/oauth/access_token")
    print(json.dumps(oauth_tokens, indent=1))


if __name__ == "__main__":
    get_oauth_tokens()