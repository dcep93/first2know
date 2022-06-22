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


async def init():
    return
    # https://playwright.dev/python/docs/intro
    from playwright.async_api import async_playwright as p  # type: ignore

    entered = p().__aenter__()
    Vars._browser = await entered.chromium.launch()


def screenshot(payload: RequestPayload) -> ResponsePayload:
    if Vars._browser is None:
        return None  # type: ignore

    context = make_context() if payload.key is None else Vars._contexts[
        payload.key]
    return _screenshot_helper(context, payload)


# TODO dcep93 make robust
def _screenshot_helper(
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
    page = context.new_page()
    page.set_extra_http_headers(params)
    page.goto(payload.url)
    evaluate = None if payload.evaluate is None else str(
        page.evaluate(payload.evaluate))
    locator = page if payload.selector is None else page.locator(
        payload.selector)
    locator.screenshot(path="screenshot.png")
    data = open("screenshot.png", "rb").read()
    data = base64.b64encode(data).decode('utf-8')
    if payload.key is None:
        context.close()
    print(
        time.time() - s,
        f"Screenshot of size {len(data)} bytes",
        f"from {payload.url}",
    )
    return ResponsePayload(data=data, evaluate=evaluate)
