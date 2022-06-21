import json
import os

from pydantic import BaseModel


class Secrets(BaseModel):
    api_key: str
    api_key_secret: str
    client_id: str
    client_secret: str
    oauth_token: str
    oauth_token_secret: str


class Vars:
    secrets: Secrets
    is_remote: bool = True


def load_local():
    Vars.is_remote = False
    client_secret_path = os.path.join(
        os.path.dirname(__file__),
        "secrets.json",
    )
    with open(client_secret_path) as fh:
        Vars.secrets = Secrets(**json.load(fh))
