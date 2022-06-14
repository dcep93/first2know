import asyncio
import typing

import concurrent.futures

import modal

import firebase_wrapper
import screenshot
import twitter_wrapper

CONCURRENT_THREADS = 16

modal_app = screenshot.get_modal_stub()


@modal_app.function(schedule=modal.Period(days=1))
async def run_cron():
    print("run_cron")
    to_handle = await firebase_wrapper.get_to_handle()
    with concurrent.futures.ThreadPoolExecutor(CONCURRENT_THREADS) as executor:
        handled = executor.map(lambda source: handle(**source), to_handle)

    for h in handled:
        await h
    print("done")

async def handle(
    url: str,
    fetch_params: typing.Dict[str, str],
    css_selector: typing.Optional[str],
    img_data: bytes,
    key: str,
    user: str,
):
    screenshot_coroutine = screenshot.screenshot(url, css_selector, fetch_params)
    current_data = await asyncio.wait_for(screenshot_coroutine, 60.0)

    if current_data is None:
        return
    if img_data == current_data:
        return

    firebase_coroutine = firebase_wrapper.write(key, current_data)
    twitter_coroutine = twitter_wrapper.tweet(user, current_data)
    await firebase_coroutine
    await twitter_coroutine
