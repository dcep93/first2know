import collections
import functools
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

# update version to clear errors
VERSION = "6.2.0"

NUM_SCREENSHOTTERS = 2

DEBOUNCE_SECONDS = 5 * 60

LOOP_SLEEP_SECONDS = 10


def init() -> None:
    firebase_wrapper.init()
    firebase_wrapper.wait_10s_for_data()


class Vars:
    _process = psutil.Process(os.getpid())
    _token: str
    running = False
    is_just_cron = False
    count = 0
    write_count = 0
    latest_time = 0.0
    latest_result: list[str] = []
    counts = collections.defaultdict[str, int](int)


def main() -> None:
    Vars.is_just_cron = True
    init()
    screenshot_manager = screenshot.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )
    try:
        run(screenshot_manager)
    finally:
        screenshot_manager.close()
    print(Vars.latest_result)


def get_memory_mb() -> float:
    return Vars._process.memory_info().rss / 1000000


def loop() -> bool:
    screenshot_manager = screenshot.Manager(
        screenshot.Screenshot,
        NUM_SCREENSHOTTERS,
    )
    try:
        rval = loop_with_manager(screenshot_manager)
    finally:
        screenshot_manager.close()
    return rval


F = typing.TypeVar("F", bound=typing.Callable[..., typing.Any])


def running_decorator(f: F) -> F:
    @functools.wraps(f)
    def g(*args: typing.Any, **kwargs: typing.Any) -> F:
        Vars.running = True
        try:
            return f(*args, **kwargs)
        finally:
            Vars.running = False

    return typing.cast(F, g)


@running_decorator
def loop_with_manager(
    screenshot_manager: screenshot.Manager,
) -> bool:
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
        time.sleep(LOOP_SLEEP_SECONDS)


# refresh token is not actually used to auth anymore
# it's still used to detect if a new cron has been spun up and taken over
def refresh_access_token() -> str:
    logger.log("refresh_access_token.start")
    new_token = str(time.time())
    firebase_wrapper.write_token(new_token)
    logger.log("refresh_access_token.end")
    return new_token


def run(screenshot_manager: screenshot.Manager) -> typing.List[str]:
    Vars.latest_time = time.time()
    Vars.count += 1
    to_handle_arr = firebase_wrapper.get_to_handle()
    Vars.latest_result.append("- run")
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
    screenshot_manager: screenshot.Manager,
) -> str:
    timer = screenshot.Timer(value=[])
    result = helper(to_handle, screenshot_manager, timer)
    Vars.counts[result] += 1
    rval = f"{result} - {to_handle.key} - {sum([v[1] for v in timer.value])} - {timer.value}"
    Vars.latest_result.append(rval)
    return rval


def helper(
    to_handle: firebase_wrapper.ToHandle,
    screenshot_manager: screenshot.Manager,
    timer: screenshot.Timer,
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

    url_message = (
        "no_url" if not to_handle.data_input.url else f"url: {to_handle.data_input.url}"
    )

    subject = f"first2know: {url_message} {to_handle.key}"

    evaluation = (
        None
        if data_output.screenshot_data is None
        else data_output.screenshot_data.evaluation
    )

    request = screenshot.Request(
        key=to_handle.key or "cron.impossible",
        data_input=to_handle.data_input,
        evaluation=evaluation,
        timer=timer,
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
        traceback_err = traceback.format_exc()
        err_str = f"traceback_err: {type(e)}: {e}\n{traceback_err}"
        if not ignorable_exception is None:
            logger.log(err_str)
            return str(ignorable_exception)
        data_output.error = firebase_wrapper.ErrorType(
            version=VERSION, time=time.time(), message=err_str
        )
        to_handle.data_output = data_output
        firebase_wrapper.write_data(to_handle)
        text = "\n".join(
            [
                str(type(e)),
                url_message,
                f"https://first2know.web.app/{to_handle.key}",
            ]
        )
        err_img_data = screenshot.str_to_binary_data(err_str)
        if Vars.is_just_cron:
            return "error"
        email_wrapper.send_email(
            to_handle.user,
            subject,
            text,
            err_img_data,
        )
        raise e

    if screenshot_response.evaluation == exceptions.IGNORE:
        return screenshot_response.evaluation

    old_md5 = (
        None if data_output.screenshot_data is None else data_output.screenshot_data.md5
    )
    if screenshot_response.md5 == old_md5:
        if data_output.error is not None:
            data_output.error = None
            to_handle.data_output = data_output
            firebase_wrapper.write_data(to_handle)
        return "old_md5"

    logger.log(f"cron.log.md5 {screenshot_response.md5} {old_md5}")

    # old_data_str = (
    #     to_handle.data_output.model_dump_json() if to_handle.data_output else ""
    # )
    to_handle.data_output = firebase_wrapper.DataOutput(
        screenshot_data=firebase_wrapper.ScreenshotData(
            md5=screenshot_response.md5,
            evaluation=screenshot_response.evaluation,
        ),
        time=now + DEBOUNCE_SECONDS,
        error=None,
    )

    text = "\n\n".join(
        [
            url_message,
            f"https://first2know.web.app/{to_handle.key}",
            # json.dumps(
            #     {"to_handle": to_handle.model_dump_json(), "old_data": old_data_str},
            #     indent=2,
            # ),
        ]
    )

    Vars.write_count += 1

    email_wrapper.send_email(
        to_handle.user,
        subject,
        text,
        screenshot_response.img_data,
    )

    logger.log(
        f"cron.log.handled {to_handle.key} {to_handle.data_output.model_dump_json()}"
    )

    firebase_wrapper.write_data(to_handle)

    return "write_data"


if __name__ == "__main__":
    main()
