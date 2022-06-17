import requests
import typing


async def proxy(url: str, fetch_params: typing.Dict[str, typing.Any]) -> str:
    headers = fetch_params.get("headers")
    data = fetch_params.get("data")
    resp = requests.get(
        url,
        headers=headers,
        data=data,
    )
    return resp.text
