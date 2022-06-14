import asyncio
import io
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

import modal

import recorded_sha

web_app = FastAPI()
modal_app = modal.App(image = modal.DebianSlim(
    extra_commands=[
        "apt-get install -y software-properties-common",
        "apt-add-repository non-free",
        "apt-add-repository contrib",
        "apt-get update",
        "pip install playwright==1.20.0",
        "playwright install-deps chromium",
        "playwright install chromium",
    ],
))


async def screenshot_get(url):
    from playwright.async_api import async_playwright # type: ignore

    async with async_playwright() as p:
        print("Fetching url", url)
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.screenshot(path="screenshot.png")
        await browser.close()
        data = open("screenshot.png", "rb").read()
        print("Screenshot of size %d bytes" % len(data))
        return data



@web_app.get("/warm")
async def warm(request: Request):
    return HTMLResponse(f'<pre>{recorded_sha.recorded_sha}</pre>')


@web_app.get("/echo/{url:path}")
async def echo(url: str):
    return HTMLResponse(url)


@web_app.get("/screenshot_info/{url:path}")
async def screenshot_info(url: str):
    try:
        img_data = await asyncio.wait_for(screenshot_get(url), 60.0)
        return len(img_data)
    except Exception:
        traceback.print_exc()
        return None


@web_app.get("/screenshot/{url:path}")
async def screenshot(url: str):
    try:
        img_data = await asyncio.wait_for(screenshot_get(url), 60.0)
        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")
    except Exception:
        traceback.print_exc()
        return None


@modal_app.asgi()
def app():
    return web_app
