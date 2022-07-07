import time

import concurrent.futures

from . import firebase_wrapper
from . import manager
from . import screenshot
from . import twitter_wrapper

# update version to clear errors
VERSION = '1.0'

NUM_SCREENSHOTTERS = 8


class Vars:
    _token: str
    _screenshot_manager: manager.Manager


def main():
    init()
    try:
        run_cron()
    finally:
        Vars._screenshot_manager.close()
    print("success")


def init():
    firebase_wrapper.init()
    Vars._screenshot_manager = manager.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )
    Vars._token = refresh_access_token()


def loop(period_seconds: int, grace_period_seconds: int) -> bool:
    def helper():
        start = time.time()
        end = start + period_seconds + grace_period_seconds
        loops = 0
        while time.time() < end:
            loops_per = loops / (time.time() - start)
            loops += 1
            if loops % 10 == 0:
                print(loops, "loops", f"{loops_per:.2f}/s")

            # exit if another process has spun up to take over
            new_token = firebase_wrapper.get_token()
            if new_token != Vars._token:
                print("exiting cron", loops)
                return True

            run_cron()
        return False

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


def run_cron():
    to_handle_arr = firebase_wrapper.get_to_handle()
    with concurrent.futures.ThreadPoolExecutor(NUM_SCREENSHOTTERS) as executor:
        executor.map(handle, to_handle_arr)


def handle(to_handle: firebase_wrapper.ToHandle) -> None:
    previous_error = to_handle.data_output.error
    if previous_error is not None and previous_error.version == VERSION:
        return

    evaluation = None \
        if to_handle.data_output.screenshot_data is None \
        else to_handle.data_output.screenshot_data.evaluation

    request = screenshot.Request(
        data_input=to_handle.data_input,
        evaluation=evaluation,
    )

    try:
        screenshot_response = Vars._screenshot_manager.run(request)
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

    old_md5 = None \
        if to_handle.data_output.screenshot_data is None \
        else to_handle.data_output.screenshot_data.md5
    if screenshot_response.md5 == old_md5:
        return

    img_url = twitter_wrapper.tweet(
        to_handle.user.screen_name,
        screenshot_response.img_data,
    )

    to_write = firebase_wrapper.DataOutput(
        screenshot_data=firebase_wrapper.ScreenshotData(
            img_url=img_url,
            md5=screenshot_response.md5,
            evaluation=screenshot_response.evaluation,
        ),
        times=to_handle.data_output.times + [time.time()],
    )

    firebase_wrapper.write_data(to_handle.key, to_write)


if __name__ == "__main__":
    main()
