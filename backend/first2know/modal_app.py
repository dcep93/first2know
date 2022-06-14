import asyncio
import io
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

import recorded_sha
import screenshot

web_app = FastAPI()
modal_app = screenshot.get_modal_stub()


@web_app.get("/")
async def get_(request: Request):
    return HTMLResponse(f'<pre>{recorded_sha.recorded_sha}</pre>')


@web_app.get("/echo/{url:path}")
async def get_echo(url: str):
    return HTMLResponse(url)


@web_app.get("/screenshot_info/{url:path}")
async def get_screenshot_info(url: str):
    try:
        img_data = await asyncio.wait_for(screenshot.screenshot(url), 60.0)
        return len(img_data)
    except Exception:
        traceback.print_exc()
        return None


@web_app.get("/screenshot/{url:path}")
async def get_screenshot(url: str):
    try:
        img_data = await asyncio.wait_for(screenshot.screenshot(url), 60.0)
        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")
    except Exception:
        traceback.print_exc()
        return None


@modal_app.asgi()
def app():
    return web_app
