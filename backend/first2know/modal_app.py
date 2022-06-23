import json
import time
import os

import modal

PERIOD_SECONDS = 60 * 15
GRACE_PERIOD_SECONDS = 60

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


# TODO akshat - would be nice if logs were bucketed
# TODO akshat Task failed with exception:
# task exited with failure, status = exit status: 101
@modal_app.function(
    schedule=modal.Period(seconds=PERIOD_SECONDS),
    secret=modal.ref("first2know_s"),
)
def modal_cron():
    print("starting modal_cron")
    init()
    cron.init()
    end = time.time() + (PERIOD_SECONDS) + GRACE_PERIOD_SECONDS
    while time.time() < end:
        should_continue = cron.run_cron()
        if not should_continue:
            print("exiting modal_cron")
            return
    raise Exception("no_exit modal_cron")


def init():
    raw_json = os.environ["secrets.json"]
    secrets.Vars.secrets = secrets.Secrets(**json.loads(raw_json))


@modal_app.asgi(secret=modal.ref("first2know_s"))
def app():
    print("starting server")
    init()
    return server.web_app
