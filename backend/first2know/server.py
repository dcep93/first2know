import base64
import json
import io
import uuid
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

from . import cron
from . import firebase_wrapper
from . import proxy
from . import recorded_sha
from . import screenshot
from . import secrets
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
    payload: str


@web_app.post("/encrypt")
def post_encrypt(payload: EncryptPayload):
    encrypted = firebase_wrapper.encrypt(payload.payload)
    return HTMLResponse(encrypted)


@web_app.post("/screenshot_img")
def post_screenshot_img(payload: screenshot.RequestPayload):
    key = str(uuid.uuid1())
    try:
        screenshot_response = screenshot.AsyncScreenshot().screenshot(
            key,
            payload,
        )
        bytes = base64.b64decode(screenshot_response.img_data)
        return StreamingResponse(io.BytesIO(bytes), media_type="image/png")
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)


@web_app.post("/screenshot_len")
def post_screenshot_len(payload: screenshot.RequestPayload):
    key = str(uuid.uuid1())
    try:
        screenshot_response = screenshot.AsyncScreenshot().screenshot(
            key,
            payload,
        )
        screenshot_response.img_data = str(len(screenshot_response.img_data))
        return HTMLResponse(screenshot_response.json())
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)


@web_app.post("/screenshot")
def post_screenshot(payload: screenshot.RequestPayload):
    key = str(uuid.uuid1())
    try:
        screenshot_response = screenshot.AsyncScreenshot().screenshot(
            key,
            payload,
        )
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
    resp_json = twitter_auth.login_request_token()
    resp_str = json.dumps(resp_json)
    return HTMLResponse(resp_str)


# TwitterLogin.loginUrl auth/twitter
@web_app.post("/twitter/access_token")
def post_twitter_access_token(oauth_verifier: str, oauth_token: str):
    resp_json = twitter_auth.login_access_token(
        oauth_token,
        oauth_verifier,
    )
    raw_resp_str = json.dumps({
        "client_secret": secrets.Vars.secrets.client_secret,
        **resp_json
    })
    resp_json["encrypted"] = firebase_wrapper.encrypt(raw_resp_str)
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
