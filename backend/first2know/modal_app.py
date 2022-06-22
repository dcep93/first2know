import json
import time
import os

import modal

PERIOD_SECONDS = 60 * 60
SHUTDOWN_PERIOD_SECONDS = 10

if not modal.is_local():
    from . import cron
    from . import secrets
    from . import server

image = modal.DebianSlim().run_commands([
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "apt-get update",
]).run_commands([
    'apt install -y git',
]).pip_install([
    'grpcio==1.43.0',
]).pip_install([
    'cryptography',
    'requests',
    'requests_oauthlib',
]).run_commands([
    "pip install playwright==1.22",
    "playwright install-deps chromium",
    "playwright install chromium",
]).pip_install([
    'git+https://github.com/ozgur/python-firebase',
])
modal_app = modal.Stub(image=image)


@modal_app.function(
    schedule=modal.Period(seconds=PERIOD_SECONDS),
    secret=modal.ref("first2know_s"),
)
# TODO dcep93 no more async
async def modal_cron():
    init_client_secret()
    end = time.time() + (PERIOD_SECONDS) - SHUTDOWN_PERIOD_SECONDS
    while time.time() < end:
        await cron.run_cron()


# for now, this is both the twitter client secret and the encryption key
def init_client_secret():
    raw_json = os.environ["secrets.json"]
    secrets.Vars.secrets = secrets.Secrets(**json.loads(raw_json))


@modal_app.asgi(secret=modal.ref("first2know_s"))
def app():
    init_client_secret()
    return server.web_app
