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

NUM_SCREENSHOTTERS = 2


class Vars:
    start_time = time.time()
    screenshot_manager: manager.Manager
    health = 0


def init():
    Vars.screenshot_manager = manager.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )


web_app = FastAPI()
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    cron_age = now - cron.Vars.latest_time
    return JSONResponse(
        status_code=200 if cron_age < 300 else 599,
        content={
            "alive_age": alive_age,
            "health_count": Vars.health,
            "cron_age": cron_age,
            "cron_count": cron.Vars.count,
            "cron_results": cron.Vars.latest_result,
            "recorded_sha": recorded_sha.recorded_sha,
        },
    )


@web_app.get("/liveness_check")
def get_health():
    print("debug_log liveness_check")
    Vars.health += 1
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
        screenshot_response = Vars.screenshot_manager.run(
            screenshot.Request(
                data_input=payload,
                evaluation=payload.evaluation,
            )
        )
        resp = screenshot_response.json()
        print("responding screenshot request")
        return HTMLResponse(resp)
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(f"<pre>{err}</pre>", 500)


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
        return HTMLResponse(f"<pre>{err}</pre>", 500)


@web_app.get("/proxy/{url:path}")
def get_proxy(url: str):
    payload = proxy.Request(url=url)
    try:
        resp = proxy.proxy(payload)
        return HTMLResponse(resp)
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(f"<pre>{err}</pre>", 500)


@web_app.get("/run_cron")
def get_cron():
    try:
        s = time.time()
        results = cron.run(Vars.screenshot_manager)
        e = time.time()
        duration = e - s
        return JSONResponse({"results": results, "duration": duration})
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(f"<pre>{err}</pre>", 500)
