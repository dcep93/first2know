import requests
import typing

from pydantic import BaseModel


class RequestPayload(BaseModel):
    url: str
    selector: typing.Optional[str] = None
    params: typing.Dict[str, typing.Any] = {}


def proxy(payload: RequestPayload) -> str:
    headers = payload.params.get("headers")
    data = payload.params.get("data")
    resp = requests.get(
        payload.url,
        headers=headers,
        data=data,
    )
    return resp.text
