import asyncio
import base64
import io
import traceback
import typing

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from . import firebase_wrapper
from . import proxy
from . import recorded_sha
from . import screenshot

web_app = FastAPI()

@web_app.get("/")
async def get_(request: Request):
    return HTMLResponse(f'<pre>{recorded_sha.recorded_sha}</pre>')


# TODO dcep93 test
@web_app.get("/encrypt/{data:str}")
async def get_encrypt(data: str):
    return HTMLResponse(firebase_wrapper.encrypt(data))


# TODO dcep93 test
@web_app.post("/screenshot")
async def post_screenshot(
    url: str,
    timeout: float=60.0,
    css_selector: typing.Optional[str]=None,
    fetch_params: typing.Dict[str, str]={},
):
    try:
        img_data = await asyncio.wait_for(screenshot.screenshot(url, css_selector, fetch_params), timeout)
        img_bytes = base64.b64decode(img_data)
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
    except Exception:
        traceback.print_exc()
        return None

@web_app.post("/proxy")
async def post_proxy(
    url: str,
    timeout: float=60.0,
    fetch_params: typing.Dict[str, typing.Any]={},
):
    try:
        resp = await asyncio.wait_for(proxy.proxy(url, fetch_params), timeout)
        return HTMLResponse(resp)
    except Exception:
        traceback.print_exc()
        return None
