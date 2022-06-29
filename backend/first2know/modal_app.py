import json
import os

import modal

PERIOD_SECONDS = 60 * 15
GRACE_PERIOD_SECONDS = 60

if not modal.is_local():
    from . import cron
    from . import recorded_sha
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
]).run_commands([
    "pip install playwright==1.22",
    "playwright install-deps chromium",
    "playwright install chromium",
]).pip_install([
    'cryptography',
    'requests',
    'requests_oauthlib',
    'pillow',
    'firebase-admin',
])
modal_app = modal.Stub(image=image)


def init(s: str):
    return
    print("modal init", s, recorded_sha.recorded_sha)
    raw_json = os.environ["secrets.json"]
    secrets.Vars.secrets = secrets.Secrets(**json.loads(raw_json))


# TODO akshat - would be nice if logs were bucketed
@modal_app.function(
    schedule=modal.Period(seconds=PERIOD_SECONDS),
    secret=modal.ref("first2know_s"),
)
def modal_cron():
    init("cron")
    was_successful = cron.loop(PERIOD_SECONDS, GRACE_PERIOD_SECONDS)
    if not was_successful:
        raise Exception("no_exit modal_cron")


@modal_app.asgi(secret=modal.ref("first2know_s"))
def app():
    init("web_app")
    return server.web_app
