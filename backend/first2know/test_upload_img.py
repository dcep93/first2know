from requests_oauthlib import OAuth1Session
import base64
import os
import json

client_secret_path = os.path.join(
    os.path.dirname(__file__),
    "secrets.json",
)
with open(client_secret_path) as fh:
    j = json.load(fh)
j["encoded"] = base64.b64decode(j["data"])

oauth = OAuth1Session(
    j["oauth_token"],
    client_secret=j["oauth_token_secret"],
)
message_obj = {}
resp = oauth.post(
    'https://upload.twitter.com/1.1/media/upload.json',
    headers={
        'Content-Type': 'application/json',
    },
    data=message_obj,
    files={
        'file': ('test.jpeg', j["encoded"]),
    },
)
if resp.status_code >= 300:
    print(resp)
    print(resp.text)
    raise Exception(resp.text)
r = json.loads(resp.text)
print(r)
