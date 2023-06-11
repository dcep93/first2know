import json
import os
import time

import modal  # type: ignore

PERIOD_SECONDS = 60 * 5
GRACE_PERIOD_SECONDS = 60 * 12

dockerfile_image = modal.Image.from_dockerfile("./Dockerfile")
stub = modal.Stub(image=dockerfile_image)


def init(s: str):
    from . import recorded_sha
    from . import secrets
    print("modal init", s, recorded_sha.recorded_sha)
    raw_json = os.environ["secrets.json"]
    secrets.Vars.secrets = secrets.Secrets(**json.loads(raw_json))


@stub.function(
    schedule=modal.Period(seconds=PERIOD_SECONDS),
    timeout=PERIOD_SECONDS + (2 * GRACE_PERIOD_SECONDS),
    secret=modal.Secret.from_name("first2know_s"),
)
def modal_cron():
    from . import cron
    init("cron")
    was_successful = cron.loop(PERIOD_SECONDS, GRACE_PERIOD_SECONDS)
    if not was_successful:
        raise Exception("no_exit modal_cron")


@stub.function(secret=modal.Secret.from_name("first2know_s"), keep_warm=1)
@modal.asgi_app()
def app():
    from . import server
    init("web_app")
    server.init()
    return server.web_app
