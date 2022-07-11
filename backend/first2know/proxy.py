import requests
import typing

from pydantic import BaseModel, Field

from bs4 import BeautifulSoup


class Params(BaseModel):
    headers: typing.Dict[str, typing.Any] = {}
    data: typing.Any = None
    find: typing.Optional[str] = None
    user_agent: typing.Optional[str] = Field(None, alias="user-agent")


class Request(BaseModel):
    url: str
    params: Params = Params()  # type: ignore


def proxy(payload: Request) -> str:
    headers = dict(payload.params.headers)
    if payload.params.user_agent:
        headers["user-agent"] = payload.params.user_agent

    resp = requests.get(
        payload.url,
        headers=headers,
        data=payload.params.data,
    )
    if payload.params.find:
        soup = BeautifulSoup(resp.text, "html.parser")
        found = soup.select_one(payload.params.find)
        if not found:
            raise Exception("could not find in html")
        return found.prettify()  # type: ignore

    return resp.text
