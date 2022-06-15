import asyncio
import base64
import io
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

import firebase_wrapper
import recorded_sha
import screenshot

web_app = FastAPI()

@web_app.get("/")
async def get_(request: Request):
    return HTMLResponse(f'<pre>{recorded_sha.recorded_sha}</pre>')


@web_app.get("/encrypt/{data:str}")
async def get_encrypt(data: str):
    return HTMLResponse(firebase_wrapper.encrypt(data))


# TODO dcep93 test then remove
@web_app.get("/decrypt/{data:str}")
async def get_decrypt(data: str):
    return HTMLResponse(firebase_wrapper.decrypt(data))


@web_app.get("/echo/{url:path}")
async def get_echo(url: str):
    return HTMLResponse(url)


@web_app.get("/screenshot/{url:path}")
async def get_screenshot(url: str):
    try:
        img_data = await asyncio.wait_for(screenshot.screenshot(url, None, {}), 60.0)
        img_bytes = base64.b64decode(img_data)
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
    except Exception:
        traceback.print_exc()
        return None


@web_app.get("/screenshot_info/{url:path}")
async def get_screenshot_info(url: str):
    try:
        img_data = await asyncio.wait_for(screenshot.screenshot(url, None, {}), 60.0)
        return len(img_data)
    except Exception:
        traceback.print_exc()
        return None


@web_app.get("/screenshot_raw/{url:path}")
async def get_screenshot_raw(url: str):
    try:
        img_data = await asyncio.wait_for(screenshot.screenshot(url, None, {}), 60.0)
        return HTMLResponse(img_data)
    except Exception:
        traceback.print_exc()
        return None
