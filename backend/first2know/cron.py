import asyncio
import json
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
    url: str,
    data: typing.Optional[str],
    key: str,
    user: str,
    selector: typing.Optional[str] = None,
    e_params: typing.Optional[str] = None,
) -> None:
    if e_params is None:
        params = {}
    else:
        decrypted = firebase_wrapper.decrypt(e_params)
        params = json.loads(decrypted)
    payload = screenshot.RequestPayload(
        url=url,
        selector=selector,
        params=params,
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
