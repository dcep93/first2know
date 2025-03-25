import json
import time
import traceback
import os
import psutil  # type: ignore
import sys

import concurrent.futures
import typing

from . import exceptions
from . import firebase_wrapper
from . import manager
from . import screenshot
from . import email_wrapper
from . import logger

IGNORE = "first2know_ignore"

# update version to clear errors
VERSION = "6.0.0"

NUM_SCREENSHOTTERS = 1

DEBOUNCE_SECONDS = 5 * 60

firebase_wrapper.init()
firebase_wrapper.wait_10s_for_data()


class Vars:
    _process = psutil.Process(os.getpid())
    _token: str
    is_just_cron = sys.argv[-1].endswith("cron.py")
    count = 0
    latest_time = 0.0
    latest_result: typing.Optional[list[str]] = None


def main():
    screenshot_manager = manager.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )
    try:
        resp = run(screenshot_manager)
    finally:
        screenshot_manager.close()


def get_memory_mb():
    return Vars._process.memory_info().rss / 1000000


def loop() -> bool:
    screenshot_manager = manager.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )
    rval = loop_with_manager(screenshot_manager)
    screenshot_manager.close()
    return rval


def loop_with_manager(screenshot_manager: manager.Manager) -> bool:
    logger.log("loop_with_manager.looping")
    Vars._token = refresh_access_token()

    loops = 0
    s = time.time()
    print_freq = 1
    resp = None
    while True:
        now = time.time()
        loops += 1
        if loops % print_freq == 0:
            seconds_per = (now - s) / print_freq
            s = now
            logger.log(f"loop_with_manager.loop {loops} {seconds_per:.2f} spl {resp}")
        # exit if another process has spun up to take over
        new_token = firebase_wrapper.get_token()
        if new_token != Vars._token:
            logger.log(f"loop_with_manager.exit {loops}")
            return True

        resp = run(screenshot_manager)
        time.sleep(1)


# refresh token is not actually used to auth anymore
# it's still used to detect if a new cron has been spun up and taken over
def refresh_access_token() -> str:
    logger.log("refresh_access_token.start")
    new_token = str(time.time())
    firebase_wrapper.write_token(new_token)
    logger.log("refresh_access_token.end")
    return new_token


def run(screenshot_manager: manager.Manager) -> typing.List[str]:
    Vars.latest_time = time.time()
    Vars.count += 1
    to_handle_arr = firebase_wrapper.get_to_handle()
    with concurrent.futures.ThreadPoolExecutor(screenshot_manager.num) as executor:
        _results = executor.map(
            lambda to_handle: handle(
                to_handle,
                screenshot_manager,
            ),
            to_handle_arr,
        )
        results = list(_results)
    Vars.latest_result = results
    return results


def handle(
    to_handle: firebase_wrapper.ToHandle,
    screenshot_manager: manager.Manager,
) -> str:
    data_output = (
        firebase_wrapper.DataOutput()
        if to_handle.data_output is None
        else to_handle.data_output
    )

    now = float(time.time())
    previous_time = data_output.time
    previous_error = data_output.error

    if Vars.is_just_cron:
        logger.log(f"is_just_cron.to_handle {to_handle}")
    elif previous_error is not None and previous_error.version == VERSION:
        return "previous_error"
    elif previous_time is not None and previous_time > now:
        return "previous_time"

    subject = f"first2know: {to_handle.data_input.url} {to_handle.key}"

    evaluation = (
        None
        if data_output.screenshot_data is None
        else data_output.screenshot_data.evaluation
    )

    request = screenshot.Request(
        data_input=to_handle.data_input,
        evaluation=evaluation,
    )

    try:
        screenshot_response: screenshot.Response = screenshot_manager.run(
            request,
        )
    except Exception as e:
        ignorable_exception = exceptions.get_ignorable_exception(
            e,
            exceptions.Src.playwright_screenshot,
        )
        if not ignorable_exception is None:
            return str(ignorable_exception)
        traceback_err = traceback.format_exc()
        to_write = data_output
        to_write.error = firebase_wrapper.ErrorType(
            version=VERSION,
            time=time.time(),
            message=f"{type(e)}: {e}\n{traceback_err}",
        )
        firebase_wrapper.write_data(to_handle.key, to_write)
        text = "\n".join(
            [
                str(type(e)),
                to_handle.data_input.url,
                f"https://first2know.web.app/{to_handle.key}",
            ]
        )
        err_str = to_write.error.message
        err_img_data = screenshot.str_to_binary_data(err_str)
        if Vars.is_just_cron:
            return "error"
        email_wrapper.send_email(
            to_handle.user.email,
            subject,
            text,
            err_img_data,
        )
        raise e

    if screenshot_response.evaluation == IGNORE:
        return IGNORE

    old_md5 = (
        None if data_output.screenshot_data is None else data_output.screenshot_data.md5
    )
    if screenshot_response.md5 == old_md5:
        if data_output.error is not None:
            data_output.error = None
            firebase_wrapper.write_data(to_handle.key, data_output)
        return "old_md5"

    logger.log(f"cron.log.md5 {screenshot_response.md5} {old_md5}")

    to_write = firebase_wrapper.DataOutput(
        screenshot_data=firebase_wrapper.ScreenshotData(
            md5=screenshot_response.md5,
            evaluation=screenshot_response.evaluation,
        ),
        time=now + DEBOUNCE_SECONDS,
        error=None,
    )

    text = "\n".join(
        [
            to_handle.data_input.url,
            f"https://first2know.web.app/{to_handle.key}",
            "\n",
            json.dumps(
                {
                    "to_handle": to_handle.model_dump_json(),
                    "to_write": to_write.model_dump_json(),
                },
                indent=2,
            ),
        ]
    )

    email_wrapper.send_email(
        to_handle.user.email,
        subject,
        text,
        screenshot_response.img_data,
    )

    logger.log(f"cron.log.handled {to_handle.key} {to_write.model_dump_json()}")

    firebase_wrapper.write_data(to_handle.key, to_write)

    return "to_write"


if __name__ == "__main__":
    main()
