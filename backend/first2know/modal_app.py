import json
import os
import time

import modal  # type: ignore

PERIOD_SECONDS = 60 * 5
GRACE_PERIOD_SECONDS = 60 * 12

if not modal.is_local():
    from . import cron
    from . import recorded_sha
    from . import secrets
    from . import server

dockerfile_image = modal.Image.from_dockerfile("./Dockerfile")
modal_app = modal.Stub(image=dockerfile_image)


def init(s: str):
    print("modal init", s, recorded_sha.recorded_sha)
    raw_json = os.environ["secrets.json"]
    secrets.Vars.secrets = secrets.Secrets(**json.loads(raw_json))


# TODO akshat - can the first run always be NOW, not NOW + modal.Period
@modal_app.function(
    schedule=modal.Period(seconds=PERIOD_SECONDS),
    secret=modal.Secret.from_name("first2know_s"),
)
def modal_cron():
    return
    init("cron")
    cron.init()
    time.sleep(10)
    was_successful = cron.loop(PERIOD_SECONDS, GRACE_PERIOD_SECONDS)
    if not was_successful:
        raise Exception("no_exit modal_cron")


@modal_app.asgi(secret=modal.Secret.from_name("first2know_s"), keep_warm=True)
def app():
    init("web_app")
    # server.init()
    return server.web_app
