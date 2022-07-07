import time

from . import firebase_wrapper
from . import screenshot
from . import twitter_wrapper

# update version to clear errors
VERSION = '1.0'


class Vars:
    _token: str
    _screenshot: screenshot._Screenshot


def main():
    init()
    run_cron()
    print("success")


def init():
    firebase_wrapper.init()
    Vars._screenshot = screenshot.SyncScreenshot()
    Vars._token = refresh_access_token()


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
def refresh_access_token() -> str:
    print("refreshing token")
    new_token = str(time.time())
    firebase_wrapper.write_token(new_token)
    print("token refreshed")
    return new_token


def run_cron() -> bool:
    # if another process has spun up to take over, exit early
    new_token = firebase_wrapper.get_token()
    if new_token != Vars._token:
        return False

    to_handle_arr = firebase_wrapper.get_to_handle()

    # TODO dcep93 queue
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

    img_url = twitter_wrapper.tweet(
        to_handle.user.screen_name,
        screenshot_response.img_data,
    )

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
