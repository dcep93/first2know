# from first2know import cron, server

# app = server.web_app

import time

from fastapi import FastAPI, Request, Response  # type: ignore
from fastapi.responses import HTMLResponse  # type: ignore

from first2know import recorded_sha

app = FastAPI()


@app.get("/")
def get_():
    return HTMLResponse(recorded_sha.recorded_sha)


@app.get("/_ae/health")
def get_ae_health():
    return
    now = time.time()
    alive_age = now - server.Vars.start_time
    cron_age = now - cron.Vars.latest
    return JSONResponse(
        status_code=200 if alive_age < 60 or cron_age < 30 else 500,
        content={"alive_age": alive_age, "cron_age": cron_age},
    )
