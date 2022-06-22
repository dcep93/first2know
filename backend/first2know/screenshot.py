import asyncio
import base64
import collections
import time
import typing

from pydantic import BaseModel


class RequestPayload(BaseModel):
    key: typing.Optional[str] = None
    url: str
    cookie: typing.Optional[str] = None
    params: typing.Optional[typing.Dict[str, str]] = None
    evaluate: typing.Optional[str] = None
    selector: typing.Optional[str] = None


class ResponsePayload(BaseModel):
    data: str
    evaluate: typing.Optional[str]


def make_context():
    return Vars._browser.new_context()


class Vars:
    _browser: typing.Any = None
    _contexts = collections.defaultdict(make_context)


# TODO dcep93 experiment with sync
def init():
    # https://playwright.dev/python/docs/intro
    from playwright.async_api import async_playwright as p  # type: ignore
    entered = asyncio.run(p().__enter__())
    Vars._browser = asyncio.run(entered.chromium.launch())


async def screenshot(payload: RequestPayload) -> ResponsePayload:
    if Vars._browser is None:
        return None  # type: ignore

    context = make_context() if payload.key is None else Vars._contexts[
        payload.key]
    return await _screenshot_helper(context, payload)


async def _screenshot_helper(
    context,
    payload: RequestPayload,
) -> ResponsePayload:
    s = time.time()
    params = {} if payload.params is None else dict(payload.params)
    if payload.cookie is not None:
        params["cookie"] = payload.cookie

    print(
        "Fetching url",
        payload.url,
    )
    page = await timeit("new_page", context.new_page())
    await timeit("set_headers", page.set_extra_http_headers(params))
    await timeit("goto", page.goto(payload.url))
    evaluate = None if payload.evaluate is None else str(await page.evaluate(
        payload.evaluate))
    locator = page if payload.selector is None else page.locator(
        payload.selector)
    await timeit("screenshot", locator.screenshot(path="screenshot.png"))
    data = open("screenshot.png", "rb").read()
    data = base64.b64encode(data).decode('utf-8')
    if payload.key is None:
        await timeit("closing", context.close())
    print(
        time.time() - s,
        f"Screenshot of size {len(data)} bytes",
        f"from {payload.url}",
    )
    return ResponsePayload(data=data, evaluate=evaluate)


async def timeit(name: str, f):
    start = time.time()
    g = await f
    print(time.time() - start, name)
    return g
