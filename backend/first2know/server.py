import json
import time
import traceback
import typing

from fastapi import FastAPI, Request, Response  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.responses import JSONResponse, HTMLResponse  # type: ignore

from firebase_admin import auth  # type: ignore

from . import cron
from . import crypt
from . import email_wrapper
from . import logger
from . import firebase_wrapper
from . import manager
from . import proxy
from . import recorded_sha
from . import screenshot

NUM_SCREENSHOTTERS = 1
MAX_CRON_AGE = 300

process = cron.psutil.Process(cron.os.getpid())


class Vars:
    start_time = time.time()
    screenshot_manager: screenshot.Manager
    health = 0


def init() -> None:
    cron.init()
    Vars.screenshot_manager = screenshot.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )
    email_wrapper.send_text_email(
        "dcep93@gmail.com",
        "startup",
        recorded_sha.recorded_sha,
    )


web_app = FastAPI()
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# # known issue: RuntimeError: Event loop is closed
# @web_app.on_event("shutdown")
# def shutdown():
#     Vars._screenshot_manager.close()


@web_app.get("/")
def get_() -> JSONResponse:
    now = time.time()
    alive_age_s = now - Vars.start_time
    cron_age = now - cron.Vars.latest_time
    mem_mb = process.memory_info().rss / (1024**2)
    status_code = 200 if cron.Vars.running and cron_age < MAX_CRON_AGE else 530
    content = {
        "write_count": cron.Vars.write_count,
        "alive_age_s": alive_age_s,
        "alive_age_h": alive_age_s / 3600,
        "health_count": Vars.health,
        "avg_cron_age": alive_age_s / (cron.Vars.count + 1),
        "cron_age": cron_age,
        "cron_count": cron.Vars.count,
        "cron_results": cron.Vars.latest_result,
        "cron_running": cron.Vars.running,
        "status_code": status_code,
        "mem_mb": mem_mb,
        "counts": cron.Vars.counts,
        "recorded_sha": recorded_sha.recorded_sha,
    }
    logger.log(f"get_ {json.dumps(content)}")
    return JSONResponse(
        status_code=status_code,
        content=content,
    )


@web_app.get("/health")
def get_health() -> JSONResponse:
    Vars.health += 1
    return get_()


@web_app.get("/start_time")
def get_start_time() -> Response:
    return Response(Vars.start_time)


class ScreenshotPayload(firebase_wrapper.DataInput):
    evaluation: typing.Optional[str]


@web_app.post("/screenshot")
def post_screenshot(payload: ScreenshotPayload) -> JSONResponse:
    logger.log("server.screenshot.receive")
    try:
        screenshot_response = Vars.screenshot_manager.run(
            screenshot.Request(
                key=f"post: {time.time()}",
                data_input=payload,
                evaluation=payload.evaluation,
            )
        )
        resp = screenshot_response.dict()
        logger.log("server.screenshot.respond")
        return JSONResponse(resp)
    except Exception:
        err = traceback.format_exc()
        return JSONResponse({"err": err}, 500)


@web_app.post("/proxy")
def post_proxy(payload: proxy.Request) -> HTMLResponse:
    try:
        resp = proxy.proxy(payload)
        return HTMLResponse(resp)
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(f"<pre>{err}</pre>", 500)


@web_app.get("/proxy/{url:path}")
def get_proxy(url: str) -> HTMLResponse:
    payload = proxy.Request(url=url)
    try:
        resp = proxy.proxy(payload)
        return HTMLResponse(resp)
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(f"<pre>{err}</pre>", 500)


@web_app.get("/run_cron")
def get_cron() -> Response:
    try:
        s = time.time()
        results = cron.run(Vars.screenshot_manager)
        e = time.time()
        duration = e - s
        return JSONResponse({"results": results, "duration": duration})
    except Exception:
        err = traceback.format_exc()
        return HTMLResponse(f"<pre>{err}</pre>", 500)


@web_app.post("/login")
async def login(request: Request) -> Response:
    data = await request.json()
    token = data.get("token")
    decoded = auth.verify_id_token(token)
    email = decoded["email"]
    fernet_key_bytes = crypt.get_fernet_key_bytes(email)
    fernet_key_str = fernet_key_bytes.decode("utf-8")
    return JSONResponse(
        status_code=200,
        content={
            "email": email,
            "fernet_key_str": fernet_key_str,
        },
    )
