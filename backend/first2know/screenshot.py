import base64
import time
import typing

from pydantic import BaseModel

from . import secrets


class RequestPayload(BaseModel):
    url: str
    cookie: typing.Optional[str] = None
    params: typing.Optional[typing.Dict[str, str]] = None
    evaluate: typing.Optional[str] = None
    selector: typing.Optional[str] = None


class ResponsePayload(BaseModel):
    data: str
    evaluate: typing.Optional[str]


def screenshot(payload: RequestPayload) -> ResponsePayload:
    if not secrets.Vars.is_remote:
        return None  # type: ignore

    start = time.time()

    params = {} if payload.params is None else dict(payload.params)
    if payload.cookie is not None:
        params["cookie"] = payload.cookie

    # https://playwright.dev/python/docs/intro
    from playwright.sync_api import sync_playwright as __p__  # type: ignore

    print(time.time() - start, "withing")

    with __p__() as p:
        print(
            time.time() - start,
            "Fetching url",
            payload.url,
        )
        browser = p.chromium.launch()
        print(
            time.time() - start,
            "paging",
        )
        page = browser.new_page()
        page.set_extra_http_headers(params)
        print(
            time.time() - start,
            "going to",
        )
        page.goto(payload.url)
        print(
            time.time() - start,
            "evaluating",
        )
        evaluate = None if payload.evaluate is None else str(
            page.evaluate(payload.evaluate))
        locator = page if payload.selector is None else page.locator(
            payload.selector)
        print(
            time.time() - start,
            "screenshotting",
        )
        locator.screenshot(path="screenshot.png")
        print(
            time.time() - start,
            "closing",
        )
        browser.close()
        data = open("screenshot.png", "rb").read()
        print(
            time.time() - start,
            f"Screenshot of size {len(data)} bytes",
            f"from {payload.url}",
        )
        data = base64.b64encode(data).decode('utf-8')
        return ResponsePayload(data=data, evaluate=evaluate)
