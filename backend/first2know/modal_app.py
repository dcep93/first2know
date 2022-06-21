import json
import os

import modal

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
    "pip install playwright==1.22",
    "playwright install-deps chromium",
    "playwright install chromium",
]).run_commands([
    'apt install -y git',
]).pip_install([
    'git+https://github.com/ozgur/python-firebase',
    'cryptography',
    'requests',
    'requests_oauthlib',
])
modal_app = modal.Stub(image=image)


# TODO dcep93 busy loop
@modal_app.function(
    schedule=modal.Period(days=1),
    secret=modal.ref("first2know_s"),
)
async def modal_cron():
    init_client_secret()
    await cron.run_cron()


# for now, this is both the twitter client secret and the encryption key
def init_client_secret():
    raw_json = os.environ["secrets.json"]
    secrets.Vars.secrets = secrets.Secrets(**json.loads(raw_json))


@modal_app.asgi(secret=modal.ref("first2know_s"))
def app():
    init_client_secret()
    return server.web_app
