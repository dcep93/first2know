import asyncio
import base64
import io
import traceback
import typing

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

from pydantic import BaseModel

from . import firebase_wrapper
from . import proxy
from . import recorded_sha
from . import screenshot


class ScreenshotPayload(BaseModel):
    url: str
    timeout: float = 60.0
    css_selector: typing.Optional[str] = None
    fetch_params: typing.Dict[str, str] = {}


class ProxyPayload(BaseModel):
    url: str
    timeout: float = 60.0
    fetch_params: typing.Dict[str, typing.Any] = {}


web_app = FastAPI()
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@web_app.get("/")
async def get_(request: Request):
    return HTMLResponse(f'<pre>{recorded_sha.recorded_sha}</pre>')


@web_app.get("/encrypt/{data:str}")
async def get_encrypt(data: str):
    return HTMLResponse(firebase_wrapper.encrypt(data))


@web_app.post("/screenshot")
async def post_screenshot(payload: ScreenshotPayload):
    try:
        img_data = await asyncio.wait_for(
            screenshot.screenshot(
                payload.url,
                payload.css_selector,
                payload.fetch_params,
            ), payload.timeout)
        img_bytes = base64.b64decode(img_data)
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
    except Exception:
        traceback.print_exc()
        return None


@web_app.post("/proxy")
async def post_proxy(payload: ProxyPayload):
    try:
        resp = await asyncio.wait_for(
            proxy.proxy(
                payload.url,
                payload.fetch_params,
            ), payload.timeout)
        return HTMLResponse(resp)
    except Exception:
        traceback.print_exc()
        return None
