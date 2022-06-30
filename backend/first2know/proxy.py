import requests
import typing

from pydantic import BaseModel


class Request(BaseModel):
    url: str
    params: typing.Dict[str, typing.Any] = {}


def proxy(payload: Request) -> str:
    headers = payload.params.get("headers")
    data = payload.params.get("data")
    resp = requests.get(
        payload.url,
        headers=headers,
        data=data,
    )
    return resp.text
