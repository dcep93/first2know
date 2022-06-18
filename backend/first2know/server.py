import asyncio
import base64
import io
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

from . import firebase_wrapper
from . import proxy
from . import recorded_sha
from . import screenshot

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
async def post_screenshot(payload: screenshot.ScreenshotPayload):
    try:
        data = await asyncio.wait_for(
            screenshot.screenshot(payload),
            payload.timeout,
        )
        bytes = base64.b64decode(data)
        return StreamingResponse(io.BytesIO(bytes), media_type="image/png")
    except Exception:
        traceback.print_exc()
        return None


@web_app.post("/screenshot_b64")
async def post_screenshot_b64(payload: screenshot.ScreenshotPayload):
    try:
        data = await asyncio.wait_for(
            screenshot.screenshot(payload),
            payload.timeout,
        )
        return HTMLResponse(data)
    except Exception:
        traceback.print_exc()
        return None


@web_app.post("/proxy")
async def post_proxy(payload: proxy.ProxyPayload):
    try:
        resp = await asyncio.wait_for(proxy.proxy(payload), payload.timeout)
        return HTMLResponse(resp)
    except Exception:
        traceback.print_exc()
        return None
