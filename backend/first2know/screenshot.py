import base64
import time
import typing

from pydantic import BaseModel

from . import secrets


class RequestPayload(BaseModel):
    timeout: float = 60.0
    url: str
    cookie: typing.Optional[str] = None
    params: typing.Optional[typing.Dict[str, str]] = None
    evaluate: typing.Optional[str] = None
    selector: typing.Optional[str] = None


class ResponsePayload(BaseModel):
    data: str
    evaluate: typing.Optional[str]


async def screenshot(payload: RequestPayload) -> ResponsePayload:
    if not secrets.Vars.is_remote:
        return None  # type: ignore

    start = time.time()

    # https://playwright.dev/python/docs/intro
    from playwright.async_api import async_playwright  # type: ignore

    async with async_playwright() as p:
        print("Fetching url", payload.url, time.time() - start)
        browser = await p.chromium.launch()
        page = await browser.new_page()
        params = {} if payload.params is None else dict(payload.params)
        if payload.cookie is not None:
            params["cookie"] = payload.cookie
        await page.set_extra_http_headers(params)
        print("going to", time.time() - start)
        await page.goto(payload.url)
        print("evaluating", time.time() - start)
        evaluate = None if payload.evaluate is None else str(
            await page.evaluate(payload.evaluate))
        locator = page if payload.selector is None else page.locator(
            payload.selector)
        print("screenshotting", time.time() - start)
        await locator.screenshot(path="screenshot.png")
        print("closing", time.time() - start)
        await browser.close()
        print("reading", time.time() - start)
        data = open("screenshot.png", "rb").read()
        print(f"Screenshot of size {len(data)} bytes from {payload.url}")
        data = base64.b64encode(data).decode('utf-8')
        print("returning", time.time() - start)
        return ResponsePayload(data=data, evaluate=evaluate)
