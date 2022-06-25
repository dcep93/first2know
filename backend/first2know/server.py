import base64
import json
import io
import traceback

from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

from . import cron
from . import firebase_wrapper
from . import proxy
from . import recorded_sha
from . import screenshot
from . import twitter_auth

web_app = FastAPI()
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@web_app.get("/")
def get_(request: Request):
    return HTMLResponse(f'<pre>{recorded_sha.recorded_sha}</pre>')


class EncryptPayload(screenshot.RequestPayload):
    cookie: str


@web_app.post("/encrypt")
def post_encrypt(payload: EncryptPayload):
    to_encrypt = payload.json()
    encrypted = firebase_wrapper.encrypt(to_encrypt)
    return HTMLResponse(encrypted)


@web_app.post("/screenshot_img")
def post_screenshot_img(payload: screenshot.RequestPayload):
    try:
        screenshot_response = screenshot.AsyncScreenshot().screenshot(payload)
        bytes = base64.b64decode(screenshot_response.data)
        return StreamingResponse(io.BytesIO(bytes), media_type="image/png")
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)


@web_app.post("/screenshot_len")
def post_screenshot_len(payload: screenshot.RequestPayload):
    try:
        screenshot_response = screenshot.AsyncScreenshot().screenshot(payload)
        screenshot_response.data = str(len(screenshot_response.data))
        return HTMLResponse(screenshot_response.json())
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)


@web_app.post("/screenshot")
def post_screenshot(payload: screenshot.RequestPayload):
    try:
        screenshot_response = screenshot.AsyncScreenshot().screenshot(payload)
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


# TwitterLogin.requestTokenUrl auth/twitter/reverse
@web_app.post("/twitter/request_token")
def post_twitter_request_token():
    resp_text = twitter_auth.login_request_token()
    resp_json = urlparse.parse_qs(resp_text)
    resp_str = json.dumps(resp_json)
    return HTMLResponse(resp_str)


# TwitterLogin.loginUrl auth/twitter
@web_app.post("/twitter/access_token")
def post_twitter_access_token(oauth_verifier: str, oauth_token: str):
    resp_text = twitter_auth.login_access_token(
        oauth_token,
        oauth_verifier,
    )
    resp_json = urlparse.parse_qs(resp_text)
    resp_str = json.dumps(resp_json)
    return HTMLResponse(resp_str)


@web_app.get("/cron")
def get_cron():
    try:
        cron.run_cron()
        return HTMLResponse(None, 200)
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)
