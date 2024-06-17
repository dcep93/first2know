import time

from fastapi.responses import JSONResponse  # type: ignore

from first2know import cron, server

app = server.web_app


@app.get("/_ae/health")
def get_ae_health():
    now = time.time()
    alive_age = now - server.Vars.start_time
    cron_age = now - cron.Vars.latest
    return JSONResponse(
        status_code=200 if alive_age < 60 or cron_age < 30 else 500,
        content={"alive_age": alive_age,
                 "cron_age": cron_age,
                 "count": cron.Vars.count,
                 },
    )
