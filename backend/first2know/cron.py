import time
import typing

from . import firebase_wrapper
from . import screenshot
from . import twitter_wrapper


class Vars:
    _did_init: bool = False
    _refresh_token: str
    _screenshot: typing.Any


def main():
    init()
    run_cron()


def init():
    firebase_wrapper.init()
    refresh_access_token()
    Vars._screenshot = screenshot.SyncScreenshot()
    Vars._did_init = True


def loop(period_seconds: int, grace_period_seconds: int):
    init()
    start = time.time()
    end = start + period_seconds + grace_period_seconds
    loops = 0
    while time.time() < end:
        loops_per = loops / (time.time() - start)
        loops += 1
        print(loops, "loops", f"{loops_per:.2f}/s")
        try:
            should_continue = run_cron()
        except Exception as e:
            print(e)
            time.sleep(1)
            continue
        if not should_continue:
            print("exiting cron", loops)
            return


# refresh token is not actually used to auth anymore
# it's still used to detect if a new cron has been spun up and taken over
def refresh_access_token():
    print("refreshing access token")
    old_refresh_token = firebase_wrapper.get_refresh_token()
    rval = twitter_wrapper.refresh_access_token(old_refresh_token)
    _, Vars._refresh_token = rval
    firebase_wrapper.write_refresh_token(Vars._refresh_token)
    print("access token refreshed")


def run_cron() -> bool:
    if not Vars._did_init:
        raise Exception("need to init")

    # if another process has spun up to take over, exit early
    new_refresh_token = firebase_wrapper.get_refresh_token()
    if new_refresh_token != Vars._refresh_token:
        return False

    to_handle = firebase_wrapper.get_to_handle()

    [i for i in map(handle, to_handle)]

    return True


def handle(to_handle: firebase_wrapper.ToHandle) -> None:
    cookie = None if to_handle.e_cookie is None else firebase_wrapper.decrypt(
        to_handle.e_cookie)
    payload = screenshot.RequestPayload(
        key=to_handle.key,
        url=to_handle.url,
        cookie=cookie,
        params=to_handle.params,
        evaluate=to_handle.evaluate,
        selector=to_handle.selector,
    )
    screenshot_response = Vars._screenshot.screenshot(payload)

    if screenshot_response is None:
        return

    current_data = screenshot_response.data
    if to_handle.data == current_data:
        return

    tweet(to_handle.user, current_data)
    firebase_wrapper.write_data(to_handle.key, current_data)


def tweet(user: str, img_data: str) -> None:
    media_id = twitter_wrapper.post_image(img_data)
    message_obj = {
        "text": f"@{user}",
        "media": {
            "media_ids": [str(media_id)]
        },
    }
    resp = twitter_wrapper.post_tweet(message_obj)
    print(resp)


if __name__ == "__main__":
    main()
