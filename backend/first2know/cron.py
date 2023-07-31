import time
import os, psutil

import concurrent.futures
import typing

from . import firebase_wrapper
from . import manager
from . import screenshot
from . import secrets
from . import twitter_wrapper

IGNORE = "first2know_ignore"

# update version to clear errors
VERSION = '3.2.1'

NUM_SCREENSHOTTERS = 8

DEBOUNCE_SECONDS = 15 * 60


class Vars:
    _process = psutil.Process(os.getpid())
    _token: str


def main():
    init()
    screenshot_manager = manager.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )
    try:
        resp = run(screenshot_manager)
        print(get_memory_mb())
    finally:
        screenshot_manager.close()
    print("success", resp)
    print(get_memory_mb())


def get_memory_mb():
    return Vars._process.memory_info().rss / 1000000


def init():
    print(get_memory_mb())
    firebase_wrapper.init()
    firebase_wrapper.wait_10s_for_data()


def loop(
    period_seconds: int,
    grace_period_seconds: int = 0,
) -> bool:
    init()
    screenshot_manager = manager.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )
    rval = loop_with_manager(
        period_seconds,
        grace_period_seconds,
        screenshot_manager,
    )
    screenshot_manager.close()
    return rval


def loop_with_manager(
    period_seconds: int,
    grace_period_seconds: int,
    screenshot_manager: manager.Manager,
) -> bool:
    Vars._token = refresh_access_token()

    start = time.time()
    end = start + period_seconds + grace_period_seconds
    loops = 0
    s = start
    print_freq = 10
    resp = None
    while time.time() < end:
        now = time.time()
        loops += 1
        if loops % print_freq == 0:
            loops_per = print_freq / (now - s)
            s = now
            print(get_memory_mb(), loops, "loops", f"{loops_per:.2f}/s", resp)
        # exit if another process has spun up to take over
        new_token = firebase_wrapper.get_token()
        if new_token != Vars._token:
            print("exiting cron", loops)
            return True

        resp = run(screenshot_manager)
        time.sleep(1)
    return False


# refresh token is not actually used to auth anymore
# it's still used to detect if a new cron has been spun up and taken over
def refresh_access_token() -> str:
    print("refreshing token")
    new_token = str(time.time())
    firebase_wrapper.write_token(new_token)
    print("token refreshed")
    return new_token


def run(screenshot_manager: manager.Manager) -> typing.List[str]:
    to_handle_arr = firebase_wrapper.get_to_handle()
    with concurrent.futures.ThreadPoolExecutor(NUM_SCREENSHOTTERS) as executor:
        _results = executor.map(
            lambda to_handle: handle(
                to_handle,
                screenshot_manager,
            ), to_handle_arr)
        results = list(_results)
    return results


def handle(
    to_handle: firebase_wrapper.ToHandle,
    screenshot_manager: manager.Manager,
) -> str:
    data_output = firebase_wrapper.DataOutput() \
        if to_handle.data_output is None \
        else to_handle.data_output

    now = float(time.time())
    previous_time = data_output.time
    previous_error = data_output.error

    if secrets.Vars.is_local:
        print("\nlocal handle", to_handle.json(), "\n")
    else:
        if previous_error is not None and previous_error.version == VERSION:
            return "previous_error"
        if previous_time is not None and previous_time > now:
            return "previous_time"

    evaluation = None \
        if data_output.screenshot_data is None \
        else data_output.screenshot_data.evaluation

    request = screenshot.Request(
        data_input=to_handle.data_input,
        evaluation=evaluation,
    )

    try:
        screenshot_response: screenshot.Response = screenshot_manager.run(
            request)
    except Exception as e:
        to_write = data_output
        to_write.error = firebase_wrapper.ErrorType(
            version=VERSION,
            time=time.time(),
            message=f'{type(e)}: {e}',
        )
        firebase_wrapper.write_data(to_handle.key, to_write)
        text = "\n".join([
            f"@{to_handle.user.screen_name}",
            str(type(e)),
            to_handle.data_input.url,
            f"https://first2know.web.app/{to_handle.key}",
        ])
        err_str = to_write.error.message
        err_img_data = screenshot.str_to_binary_data(err_str)
        img_url = twitter_wrapper.tweet(
            text,
            err_img_data,
        )
        raise e

    if screenshot_response.evaluation == IGNORE:
        return "ignore"

    old_md5 = None \
        if data_output.screenshot_data is None \
        else data_output.screenshot_data.md5
    if screenshot_response.md5 == old_md5:
        return "old_md5"

    print(screenshot_response.md5, old_md5)

    text = "\n".join([
        f"@{to_handle.user.screen_name}",
        to_handle.data_input.url,
        f"https://first2know.web.app/{to_handle.key}",
    ])

    img_url = twitter_wrapper.tweet(
        text,
        screenshot_response.img_data,
    )

    to_write = firebase_wrapper.DataOutput(
        screenshot_data=firebase_wrapper.ScreenshotData(
            img_url=img_url,
            md5=screenshot_response.md5,
            evaluation=screenshot_response.evaluation,
        ),
        time=now + DEBOUNCE_SECONDS,
        error=None,
    )

    if True or secrets.Vars.is_local:
        print(to_handle.key, to_write.json())

    firebase_wrapper.write_data(to_handle.key, to_write)

    return "to_write"


if __name__ == "__main__":
    main()
