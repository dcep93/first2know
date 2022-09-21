import time

import concurrent.futures

from . import firebase_wrapper
from . import manager
from . import screenshot
from . import secrets
from . import twitter_wrapper

IGNORE = "first2know_ignore"

# update version to clear errors
VERSION = '1.1.0'

NUM_SCREENSHOTTERS = 8


class Vars:
    _token: str
    _screenshot_manager: manager.Manager


def main():
    init()
    firebase_wrapper.wait_1s_for_data()
    try:
        count = run_cron()
    finally:
        Vars._screenshot_manager.close()
    print("success", count)


def init():
    firebase_wrapper.init()
    Vars._screenshot_manager = manager.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )


def loop(period_seconds: int, grace_period_seconds: int) -> bool:

    def helper():
        start = time.time()
        end = start + period_seconds + grace_period_seconds
        loops = 0
        s = start
        print_freq = 10
        while time.time() < end:
            now = time.time()
            loops += 1
            if loops % print_freq == 0:
                loops_per = print_freq / (now - s)
                s = now
                print(loops, "loops", f"{loops_per:.2f}/s")
            # exit if another process has spun up to take over
            new_token = firebase_wrapper.get_token()
            if new_token != Vars._token:
                print("exiting cron", loops)
                return True

            count = run_cron()
            if count == 0:
                time.sleep(1)
            # TODO dcep93 sleep properly
            time.sleep(1)
        return False

    Vars._token = refresh_access_token()
    rval = helper()
    Vars._screenshot_manager.close()
    return rval


# refresh token is not actually used to auth anymore
# it's still used to detect if a new cron has been spun up and taken over
def refresh_access_token() -> str:
    print("refreshing token")
    new_token = str(time.time())
    firebase_wrapper.write_token(new_token)
    print("token refreshed")
    return new_token


def run_cron() -> int:
    to_handle_arr = firebase_wrapper.get_to_handle()
    with concurrent.futures.ThreadPoolExecutor(NUM_SCREENSHOTTERS) as executor:
        _results = executor.map(handle, to_handle_arr)
        results = list(_results)
    return len(results)


def handle(to_handle: firebase_wrapper.ToHandle) -> None:
    # print("handle", to_handle.json())
    previous_error = to_handle.data_output.error
    if not secrets.Vars.is_local:
        if previous_error is not None and previous_error.version == VERSION:
            return

    evaluation = None \
        if to_handle.data_output.screenshot_data is None \
        else to_handle.data_output.screenshot_data.evaluation

    request = screenshot.Request(
        data_input=to_handle.data_input,
        evaluation=evaluation,
    )

    now = time.time()

    try:
        recents = [t for t in to_handle.data_output.times if now - t < 60]
        if len(recents) > 3:
            raise Exception("too many recents")
        screenshot_response = Vars._screenshot_manager.run(request)
    except Exception as e:
        to_write = to_handle.data_output
        to_write.times.append(now)
        to_write.error = firebase_wrapper.ErrorType(
            version=VERSION,
            time=now,
            message=f'{type(e)}: {e}',
        )
        firebase_wrapper.write_data(to_handle.key, to_write)
        raise e

    if screenshot_response.evaluation == IGNORE:
        return

    old_md5 = None \
        if to_handle.data_output.screenshot_data is None \
        else to_handle.data_output.screenshot_data.md5
    if screenshot_response.md5 == old_md5:
        return

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
        error=None,
        times=to_handle.data_output.times + [now],
    )

    if secrets.Vars.is_local:
        print(to_handle.key, to_write.json())

    firebase_wrapper.write_data(to_handle.key, to_write)


if __name__ == "__main__":
    main()
