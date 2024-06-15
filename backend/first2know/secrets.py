import json
import os

from pydantic import BaseModel


class Secrets(BaseModel):
    api_key: str
    api_key_secret: str
    client_id: str
    client_secret: str
    access_token: str
    access_token_secret: str
    # $ make twitter_auth
    oauth_token: str
    oauth_token_secret: str


local_secret_path = os.path.join(
    os.path.dirname(__file__),
    "secrets.json",
)
with open(local_secret_path) as fh:
    _secrets = Secrets(**json.load(fh))


class Vars:
    secrets: Secrets = _secrets
