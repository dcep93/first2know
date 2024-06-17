import json
import os
import logging
import time
import traceback
import typing

import pydantic  # type: ignore

from fastapi import FastAPI, Request, Response  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.responses import JSONResponse, HTMLResponse  # type: ignore

from . import cron
from . import firebase_wrapper
from . import manager
from . import proxy
from . import recorded_sha
from . import screenshot
from . import secrets
from . import twitter_auth

NUM_SCREENSHOTTERS = 4


class Vars:
    start_time = time.time()
    _screenshot_manager: manager.Manager = manager.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )


web_app = FastAPI()
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@web_app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Sent response: {response.status_code}")

    return response


# # known issue: RuntimeError: Event loop is closed
# @web_app.on_event("shutdown")
# def shutdown():
#     Vars._screenshot_manager.close()


@web_app.get("/")
def get_():
    now = time.time()
    alive_age = now - Vars.start_time
    cron_age = now - cron.Vars.latest
    return JSONResponse(
        status_code=200 if alive_age < 60 or cron_age < 30 else 500,
        content={
            "alive_age": alive_age,
            "cron_age": cron_age,
            "count": cron.Vars.count,
            "recorded_sha": recorded_sha.recorded_sha,
        },
    )


@web_app.get("/_ae/health")
def get_health():
    return get_()


@web_app.get("/start_time")
def get_start_time(request: Request):
    return Response(Vars.start_time)


# class PostInputPayload(firebase_wrapper.DataInput):
#     old_encrypted: typing.Optional[str]
#     evaluation: typing.Any

#     def reencrypt_cookie(self):
#         if self.old_encrypted is not None:
#             decrypted = firebase_wrapper.decrypt(self.old_encrypted)
#             data_input = firebase_wrapper.DataInput(**json.loads(decrypted))
#             decrypted_params = {} \
#                 if data_input.params is None \
#                 else data_input.params
#             cookie = decrypted_params.get("cookie")
#             if cookie is not None:
#                 params = {} \
#                     if self.params is None \
#                     else self.params
#                 params["cookie"] = cookie
#                 self.params = params


class ScreenshotPayload(firebase_wrapper.DataInput):
    evaluation: typing.Optional[str]


@web_app.post("/screenshot")
def post_screenshot(payload: ScreenshotPayload):
    print("received screenshot request")
    # payload.reencrypt_cookie()
    try:
        screenshot_response = Vars._screenshot_manager.run(
            screenshot.Request(
                data_input=payload,
                evaluation=payload.evaluation,
            ))
        resp = screenshot_response.json()
        print("responding screenshot request")
        return HTMLResponse(resp)
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)


@web_app.post("/encrypt")
def post_encrypt(payload: firebase_wrapper.DataInput):
    print("received encrypt request")
    json_str = payload.json()
    encrypted = firebase_wrapper.encrypt(json_str)
    return HTMLResponse(encrypted)


@web_app.post("/proxy")
def post_proxy(payload: proxy.Request):
    try:
        resp = proxy.proxy(payload)
        return HTMLResponse(resp)
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)


@web_app.get("/proxy/{url:path}")
def get_proxy(url: str):
    payload = proxy.Request(url=url)
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
    user = firebase_wrapper.User(
        user_id=int(resp_json["user_id"]),
        screen_name=resp_json["screen_name"],
        encrypted=secrets.Vars.secrets.client_secret,
    )
    user.encrypted = firebase_wrapper.encrypt(user.json())
    d = dict(user)
    d["double_encrypted"] = firebase_wrapper.encrypt(user.encrypted)
    return HTMLResponse(json.dumps(d))


@web_app.get("/run_cron")
def get_cron():
    try:
        cron.main()
        return HTMLResponse(None, 200)
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(err, 500)
