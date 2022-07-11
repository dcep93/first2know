import requests
import typing

from pydantic import BaseModel

from bs4 import BeautifulSoup


class Params(BaseModel):
    headers: typing.Dict[str, typing.Any] = {}
    data: typing.Any = None
    find: typing.Optional[str] = None


class Request(BaseModel):
    url: str
    params: Params = Params()


def proxy(payload: Request) -> str:
    headers = payload.params.headers
    data = payload.params.data
    resp = requests.get(
        payload.url,
        headers=headers,
        data=data,
    )
    if payload.params.find:
        soup = BeautifulSoup(resp.text, "html.parser")
        found = soup.find(payload.params.find)
        if not found:
            raise Exception("could not find in html")
        return found.prettify()  # type: ignore

    return resp.text
