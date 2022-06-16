import asyncio
import json
import os
import typing

import concurrent.futures

import modal

import firebase_wrapper
import recorded_sha
import screenshot
import twitter_wrapper

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
async def modal_cron():
    await run_cron()

# TODO dcep93 - utilize secret
# for now, this is both the twitter client secret and the encryption key
@modal_app.function(secret=modal.ref("first2know"))
def get_client_secret() -> str:
    return os.environ["client_secret"]

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
    img_data: str,
    key: str,
    user: str,
    e_fetch_params: typing.Optional[str]=None,
    css_selector: typing.Optional[str]=None,
):
    if e_fetch_params is None:
        fetch_params = {}
    else:
        decrypted = firebase_wrapper.decrypt(e_fetch_params)
        fetch_params = json.loads(decrypted)
    screenshot_coroutine = screenshot.screenshot(url, css_selector, fetch_params)
    current_data = await asyncio.wait_for(screenshot_coroutine, 60.0)

    if current_data is None:
        return
    if img_data == current_data:
        return

    firebase_wrapper.write_img_data(key, current_data)
    twitter_wrapper.tweet(user, current_data)

if __name__ == "__main__":
    asyncio.run(run_cron())
