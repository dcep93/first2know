import asyncio
import base64
import json
import sys
import typing

from pydantic import BaseModel


class ScreenshotPayload(BaseModel):
    url: str
    timeout: float = 60.0
    selector: typing.Optional[str] = None
    params: typing.Dict[str, str] = {}


async def screenshot(payload: ScreenshotPayload) -> str:
    from playwright.async_api import async_playwright  # type: ignore

    async with async_playwright() as p:
        print("Fetching url", payload.url)
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_extra_http_headers(payload.params)
        await page.goto(payload.url)
        locator = page if payload.selector is None else page.locator(
            payload.selector)
        await locator.screenshot(path="screenshot.png")
        await browser.close()
        data = open("screenshot.png", "rb").read()
        print("Screenshot of size %d bytes" % len(data))
        return base64.b64encode(data).decode('utf-8')


if __name__ == "__main__":
    args = {i: j for i, j in enumerate(sys.argv)}
    payload = ScreenshotPayload(
        url=args[1],
        timeout=float(args.get(2, 60.0)),
        selector=args.get(3),
        params=json.loads(args.get(4, '{}')),
    )
    data = asyncio.run(screenshot(payload))
    print(data)
