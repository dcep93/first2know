import requests
import typing

from pydantic import BaseModel


class ProxyPayload(BaseModel):
    timeout: float = 60.0
    url: str
    selector: typing.Optional[str] = None
    params: typing.Dict[str, typing.Any] = {}


async def proxy(payload: ProxyPayload) -> str:
    headers = payload.params.get("headers")
    data = payload.params.get("data")
    resp = requests.get(
        payload.url,
        headers=headers,
        data=data,
    )
    return resp.text
