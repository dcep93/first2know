import asyncio
import base64
import os
import io
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

from . import cron
from . import firebase_wrapper
from . import proxy
from . import recorded_sha
from . import secrets
from . import screenshot

web_app = FastAPI()
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    if os.environ.get("LOCAL_DOCKER"):
        print("loading local server")
        secrets.load_local()
        asyncio.run(screenshot.init())


@web_app.get("/")
def get_(request: Request):
    return HTMLResponse(f'<pre>{recorded_sha.recorded_sha}</pre>')


@web_app.get("/encrypt/{data:str}")
def get_encrypt(data: str):
    return HTMLResponse(firebase_wrapper.encrypt(data))


@web_app.post("/screenshot")
def post_screenshot(payload: screenshot.RequestPayload):
    try:
        screenshot_response = screenshot.screenshot(payload)
        bytes = base64.b64decode(screenshot_response.data)
        return StreamingResponse(io.BytesIO(bytes), media_type="image/png")
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)


@web_app.post("/screenshot_b64")
def post_screenshot_b64(payload: screenshot.RequestPayload):
    try:
        screenshot_response = screenshot.screenshot(payload)
        return HTMLResponse(screenshot_response.json())
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)


@web_app.post("/proxy")
def post_proxy(payload: proxy.RequestPayload):
    try:
        resp = proxy.proxy(payload)
        return HTMLResponse(resp)
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)


@web_app.get("/cron")
def get_cron():
    try:
        cron.run_cron()
        return HTMLResponse(None, 200)
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)


if __name__ == "first2know.server":
    main()
