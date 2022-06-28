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
    redirect_uri: str


class Vars:
    secrets: Secrets = None  # type: ignore
    is_local = False


if Vars.secrets is None:
    if os.environ.get("LOCAL"):
        Vars.is_local = True
        client_secret_path = os.path.join(
            os.path.dirname(__file__),
            "secrets.json",
        )
        with open(client_secret_path) as fh:
            Vars.secrets = Secrets(**json.load(fh))
