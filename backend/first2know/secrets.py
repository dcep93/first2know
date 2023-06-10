import json
import os

from pydantic import BaseModel

import modal


class Secrets(BaseModel):
    api_key: str
    api_key_secret: str
    client_id: str
    client_secret: str
    access_token: str
    access_token_secret: str


class Vars:
    secrets: Secrets = None  # type: ignore
    is_local = False


if modal.is_local():
    if Vars.secrets is None:
        Vars.is_local = True
        client_secret_path = os.path.join(
            os.path.dirname(__file__),
            "secrets.json",
        )
        with open(client_secret_path) as fh:
            Vars.secrets = Secrets(**json.load(fh))
