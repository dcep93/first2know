# from first2know import cron, server

# app = server.web_app

from fastapi import FastAPI, Request, Response  # type: ignore
from fastapi.responses import HTMLResponse  # type: ignore

app = FastAPI()


@app.get("/")
def get_(request):
    return HTMLResponse("hi")
