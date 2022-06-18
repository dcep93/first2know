import base64
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
        await page.goto(payload.url)
        await page.screenshot(path="screenshot.png")
        await browser.close()
        data = open("screenshot.png", "rb").read()
        print("Screenshot of size %d bytes" % len(data))
        return base64.b64encode(data).decode('utf-8')
