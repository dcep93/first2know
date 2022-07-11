import requests
import typing

from pydantic import BaseModel, Field

from bs4 import BeautifulSoup


class Params(BaseModel):
    headers: typing.Dict[str, typing.Any] = {}
    data: typing.Any = None
    find: typing.Optional[typing.List[str]] = None
    user_agent: typing.Optional[str] = Field(None, alias="user-agent")
    cookie: typing.Optional[str] = None


class Request(BaseModel):
    url: str
    params: Params = Params()  # type: ignore


def proxy(payload: Request) -> str:
    headers = dict(payload.params.headers)
    if payload.params.user_agent:
        headers["user-agent"] = payload.params.user_agent
    if payload.params.cookie:
        headers["cookie"] = payload.params.cookie

    resp = requests.get(
        payload.url,
        headers=headers,
        data=payload.params.data,
    )
    if payload.params.find:
        soup = BeautifulSoup(resp.text, "html.parser")

        find = ["link[rel='stylesheet']"] + payload.params.find

        found = "".join([i.prettify() for j in find for i in soup.select(j)])

        return f"<base href='{payload.url}' />\n" + found

    return resp.text
