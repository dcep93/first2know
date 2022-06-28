import time

from . import firebase_wrapper
from . import screenshot
from . import twitter_wrapper

# update version to clear errors
VERSION = '1.0'


class Vars:
    _refresh_token: str
    _screenshot: screenshot._Screenshot


def main():
    init()
    run_cron()
    print("success")


def init():
    firebase_wrapper.init()
    Vars._refresh_token = refresh_access_token()
    Vars._screenshot = screenshot.SyncScreenshot()


def loop(period_seconds: int, grace_period_seconds: int) -> bool:
    init()
    start = time.time()
    end = start + period_seconds + grace_period_seconds
    loops = 0
    while time.time() < end:
        loops_per = loops / (time.time() - start)
        loops += 1
        if loops % 10 == 0:
            print(loops, "loops", f"{loops_per:.2f}/s")
        should_continue = run_cron()
        if not should_continue:
            print("exiting cron", loops)
            return True
    return False


# refresh token is not actually used to auth anymore
# it's still used to detect if a new cron has been spun up and taken over
def refresh_access_token():
    print("refreshing access token")
    old_refresh_token = firebase_wrapper.get_refresh_token()
    rval = twitter_wrapper.refresh_access_token(old_refresh_token)
    _, refresh_token = rval
    firebase_wrapper.write_refresh_token(refresh_token)
    print("access token refreshed")
    return refresh_token


def run_cron() -> bool:
    # if another process has spun up to take over, exit early
    new_refresh_token = firebase_wrapper.get_refresh_token()
    if new_refresh_token != Vars._refresh_token:
        return False

    to_handle = firebase_wrapper.get_to_handle()

    # TODO akshat async
    [i for i in map(handle, to_handle)]

    return True


def handle(to_handle: firebase_wrapper.ToHandle) -> None:
    previous_error = to_handle.data.error
    if previous_error is not None and previous_error.version == VERSION:
        return

    now = time.time()
    screenshot_payload = screenshot.RequestPayload(
        url=to_handle.url,
        params=to_handle.params,
        evaluate=to_handle.evaluate,
        selector=to_handle.selector,
        previous_evaluation=to_handle.data.evaluation,
        evaluation_to_img=to_handle.evaluation_to_img,
    )
    try:
        screenshot_response = Vars._screenshot.screenshot(
            to_handle.key,
            screenshot_payload,
        )
    except Exception as e:
        to_write = to_handle.data
        to_write.times.append(now)
        to_write.error = firebase_wrapper.ErrorType(
            version=VERSION,
            time=now,
            message=str(e),
        )
        firebase_wrapper.write_data(to_handle.key, to_write)
        return

    to_write = firebase_wrapper.DataType(
        img_data=screenshot_response.img_data,
        evaluation=screenshot_response.evaluation,
        times=to_handle.data.times + [now],
    )

    if to_handle.data.img_data == to_write.img_data:
        return

    tweet(to_handle.user_name, to_write.img_data)
    firebase_wrapper.write_data(to_handle.key, to_write)


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
