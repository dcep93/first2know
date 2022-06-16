import os

import modal

if not modal.is_local():
    from . import cron
    from . import server

image =  modal.DebianSlim()
image.run_commands([
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "apt-get update",
    "pip install playwright==1.20.0",
    "playwright install-deps chromium",
    "playwright install chromium",
]).pip_install([
    'git+https://github.com/ozgur/python-firebase',
    'cryptography',
    'requests',
])
modal_app = modal.Stub(image=image)

@modal_app.function(schedule=modal.Period(days=1), secret=modal.ref("first2know_s"))
async def modal_cron():
    init_client_secret()
    await cron.run_cron()

# for now, this is both the twitter client secret and the encryption key
def init_client_secret():
    client_secret = os.environ["client_secret"]
    cron.Vars.client_secret = client_secret

@modal_app.asgi(image=image)
def app():
    return server.web_app
