import json
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
    Vars._screenshot = screenshot.SyncScreenshot()
    Vars._refresh_token = refresh_access_token()


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

    to_handle_arr = firebase_wrapper.get_to_handle()

    # TODO akshat async
    [i for i in map(handle, to_handle_arr)]

    return True


def handle(to_handle: firebase_wrapper.ToHandle) -> None:
    previous_error = to_handle.data_output.error
    if previous_error is not None and previous_error.version == VERSION:
        return

    evaluation = None \
        if to_handle.data_output.img_data is None \
        else to_handle.data_output.img_data.evaluation

    try:
        screenshot_response = Vars._screenshot.screenshot(
            to_handle.key,
            to_handle.data_input,
            evaluation,
        )
    except Exception as e:
        to_write = to_handle.data_output
        to_write.times.append(time.time())
        to_write.error = firebase_wrapper.ErrorType(
            version=VERSION,
            time=time.time(),
            message=str(e),
        )
        firebase_wrapper.write_data(to_handle.key, to_write)
        raise e

    img_hash = hash(screenshot_response.img_data)
    old_img_hash = None \
        if to_handle.data_output.img_data is None \
        else to_handle.data_output.img_data.img_hash
    if img_hash == old_img_hash:
        return

    text = screenshot_response.evaluation \
        if type(screenshot_response.evaluation) is str \
        else json.dumps(screenshot_response.evaluation)

    resp = twitter_wrapper.send_message(
        to_handle.user.user_id,
        text,
        screenshot_response.img_data,
    )

    img_url = resp["img_url"]

    to_write = firebase_wrapper.DataOutput(
        img_data=firebase_wrapper.ImgData(
            img_url=img_url,
            img_hash=img_hash,
            evaluation=screenshot_response.evaluation,
        ),
        times=to_handle.data_output.times + [time.time()],
    )

    firebase_wrapper.write_data(to_handle.key, to_write)


if __name__ == "__main__":
    main()
