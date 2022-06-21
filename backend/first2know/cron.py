import asyncio
import typing

import concurrent.futures

from . import firebase_wrapper
from . import recorded_sha
from . import screenshot
from . import twitter_wrapper

CONCURRENT_THREADS = 8


class Vars:
    client_secret: str = None  # type: ignore


async def run_cron() -> None:
    print(f"run_cron {recorded_sha.recorded_sha}")

    firebase_wrapper.init()
    twitter_wrapper.update_access_token()

    to_handle = firebase_wrapper.get_to_handle()
    with concurrent.futures.ThreadPoolExecutor(CONCURRENT_THREADS) as executor:
        handled = executor.map(lambda source: handle(**source), to_handle)

    for h in handled:
        await h
    print("done")


async def handle(
    key: str,
    user: str,
    url: str,
    e_cookie: typing.Optional[str] = None,
    params: typing.Optional[typing.Dict[str, typing.Any]] = None,
    evaluate: typing.Optional[str] = None,
    selector: typing.Optional[str] = None,
    data: typing.Optional[str] = None,
) -> None:
    cookie = None if e_cookie is None else firebase_wrapper.decrypt(e_cookie)
    payload = screenshot.RequestPayload(
        url=url,
        cookie=cookie,
        params=params,
        evaluate=evaluate,
        selector=selector,
    )
    screenshot_coroutine = screenshot.screenshot(payload)
    screenshot_response = await asyncio.wait_for(screenshot_coroutine, 60.0)

    if screenshot_response is None:
        return

    current_data = screenshot_response.data
    if data == current_data:
        return

    firebase_wrapper.write_data(key, current_data)
    twitter_wrapper.tweet(user, current_data)


if __name__ == "__main__":
    asyncio.run(run_cron())
