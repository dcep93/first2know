import os

import modal

import cron
import server

image =  modal.DebianSlim()
image.run_commands([
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "apt-get update",
    "pip install playwright==1.20.0",
    "playwright install-deps chromium",
    "playwright install chromium",
])
modal_app = modal.Stub(image=image)

@modal_app.function(schedule=modal.Period(days=1))
async def modal_cron():
    init_client_secret()
    await cron.run_cron()

# TODO dcep93 - utilize secret
# for now, this is both the twitter client secret and the encryption key
@modal_app.function(secret=modal.ref("first2know"))
def init_client_secret():
    client_secret = os.environ["client_secret"]
    cron.Vars.client_secret = client_secret

@modal_app.asgi()
def app():
    return server.web_app
