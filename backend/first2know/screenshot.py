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


def make_p():
    start = time.time()
    p = Vars.p_f()
    print(time.time() - start, "make_p")
    return p


class Vars:
    p_f: typing.Any = None
    ps = collections.defaultdict(make_p)


def init():
    # https://playwright.dev/python/docs/intro
    from playwright.async_api import async_playwright as p  # type: ignore
    Vars.p_f = p


async def screenshot(payload: RequestPayload) -> ResponsePayload:
    if Vars.p_f is None:
        return None  # type: ignore

    p = make_p() if payload.key is None else Vars.ps[payload.key]
    async with p as _p:
        return await _screenshot_helper(_p, payload)


async def _screenshot_helper(p, payload: RequestPayload) -> ResponsePayload:
    params = {} if payload.params is None else dict(payload.params)
    if payload.cookie is not None:
        params["cookie"] = payload.cookie

    print(
        "Fetching url",
        payload.url,
    )
    start = time.time()
    browser = await p.chromium.launch()
    print(
        time.time() - start,
        "launched",
    )
    start = time.time()
    page = await browser.new_page()
    print(
        time.time() - start,
        "new_page",
    )
    start = time.time()
    await page.set_extra_http_headers(params)
    print(
        time.time() - start,
        "set_headers",
    )
    start = time.time()
    await page.goto(payload.url)
    print(
        time.time() - start,
        "goto",
    )
    start = time.time()
    evaluate = None if payload.evaluate is None else str(await page.evaluate(
        payload.evaluate))
    locator = page if payload.selector is None else page.locator(
        payload.selector)
    print(
        time.time() - start,
        "evaluate_locator",
    )
    start = time.time()
    await locator.screenshot(path="screenshot.png")
    print(
        time.time() - start,
        "screenshot",
    )
    data = open("screenshot.png", "rb").read()
    data = base64.b64encode(data).decode('utf-8')
    if payload.key is None:
        print(
            time.time() - start,
            "closing",
        )
        await browser.close()
    print(
        time.time() - start,
        f"Screenshot of size {len(data)} bytes",
        f"from {payload.url}",
    )
    return ResponsePayload(data=data, evaluate=evaluate)
