import json
import os

from pydantic import BaseModel  # type: ignore


class Secrets(BaseModel):
    email_user: str
    email_password: str


local_secret_path = os.path.join(
    os.path.dirname(__file__),
    "secrets.json",
)
with open(local_secret_path) as fh:
    _secrets = Secrets(**json.load(fh))


class Vars:
    secrets: Secrets = _secrets
