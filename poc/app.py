import uvicorn
from fastapi import FastAPI, Request, Response  # type: ignore
from fastapi.responses import HTMLResponse  # type: ignore


web_app = FastAPI()


@web_app.get("/")
def get_(request: Request):
    return HTMLResponse("hi")


@web_app.get("/health")
def get_health(request: Request):
    return HTMLResponse("hi")


@web_app.get("/healthcheck")
def get_healthcheck(request: Request):
    return HTMLResponse("hi")


uvicorn.run(web_app, host="0.0.0.0", port=8080)
