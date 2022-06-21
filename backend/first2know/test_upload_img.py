import requests
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
message_obj = {
    "media": j["encoded"],
    # "media_data": j["data"],
    "media_category": "tweet_image"
}
resp = requests.post(
    'https://upload.twitter.com/1.1/media/upload.json',
    headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f"Bearer {j['access_token']}",
    },
    data=message_obj,
    files={
        'file': ('test.jpeg', j["encoded"]),
    },
)
if resp.status_code >= 300:
    print(resp)
    print('x')
    print(resp.text)
    print('x')
    raise Exception(resp.text)
r = json.loads(resp.text)
print(r)
