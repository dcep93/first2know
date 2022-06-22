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

    # https://playwright.dev/python/docs/intro
    from playwright.sync_api import sync_playwright as __p__  # type: ignore

    with __p__() as p:
        print("Fetching url", payload.url, time.time() - start)
        browser = p.chromium.launch()
        page = browser.new_page()
        params = {} if payload.params is None else dict(payload.params)
        if payload.cookie is not None:
            params["cookie"] = payload.cookie
        page.set_extra_http_headers(params)
        print("going to", time.time() - start)
        page.goto(payload.url)
        print("evaluating", time.time() - start)
        evaluate = None if payload.evaluate is None else str(
            page.evaluate(payload.evaluate))
        locator = page if payload.selector is None else page.locator(
            payload.selector)
        print("screenshotting", time.time() - start)
        locator.screenshot(path="screenshot.png")
        print("closing", time.time() - start)
        browser.close()
        print("reading", time.time() - start)
        data = open("screenshot.png", "rb").read()
        print(f"Screenshot of size {len(data)} bytes from {payload.url}")
        data = base64.b64encode(data).decode('utf-8')
        print("returning", time.time() - start)
        return ResponsePayload(data=data, evaluate=evaluate)
