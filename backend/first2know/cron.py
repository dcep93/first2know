import asyncio
import typing

import concurrent.futures

import modal

import firebase_wrapper
import recorded_sha
import screenshot
import twitter_wrapper

# TODO dcep93
encoded_auth = ""
refresh_token = ""

CONCURRENT_THREADS = 8

image =  modal.DebianSlim()
image.run_commands([
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "apt-get update",
    "pip install playwright==1.20.0",
    "playwright install-deps chromium",
    "playwright install chromium",
])
modal_app = modal.Stub(image=image)

@modal_app.function(schedule=modal.Period(days=1))
async def run_cron():
    print(f"run_cron {recorded_sha.recorded_sha}")

    twitter_wrapper.update_access_token(encoded_auth, refresh_token)

    to_handle = firebase_wrapper.get_to_handle()
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

    firebase_wrapper.write_img_data(key, current_data)
    twitter_wrapper.tweet(user, current_data)
