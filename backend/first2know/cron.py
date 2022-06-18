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


async def run_cron():
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
    img_data: typing.Optional[str],
    key: str,
    user: str,
    e_fetch_params: typing.Optional[str] = None,
    css_selector: typing.Optional[str] = None,
):
    if e_fetch_params is None:
        fetch_params = {}
    else:
        decrypted = firebase_wrapper.decrypt(e_fetch_params)
        fetch_params = json.loads(decrypted)
    screenshot_coroutine = screenshot.screenshot(url, css_selector,
                                                 fetch_params)
    current_data = await asyncio.wait_for(screenshot_coroutine, 60.0)

    if current_data is None:
        return
    if img_data == current_data:
        return

    firebase_wrapper.write_img_data(key, current_data)
    twitter_wrapper.tweet(user, current_data)


if __name__ == "__main__":
    asyncio.run(run_cron())
