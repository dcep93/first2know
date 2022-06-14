import asyncio
import time

import concurrent.futures

import modal

import screenshot

CONCURRENT_THREADS = 8

modal_app = screenshot.get_modal_stub()


@modal_app.function(schedule=modal.Period(minutes=1))
async def run_cron():
    print("run_cron")
    print(time.time())
    to_fetch = [
        {"url": "https://chess.com", "fetch_params": {}, "css_selector": None},
        {"url": "https://www.chess.com/member/dcep93", "fetch_params": {}, "css_selector": None},
    ]
    with concurrent.futures.ThreadPoolExecutor(CONCURRENT_THREADS) as executor:
        all_fetched = executor.map(fetch, to_fetch)

    for i, f in enumerate(all_fetched):
        fetched = await f
        print(to_fetch[i]["url"], len(fetched))
    print("done")

async def fetch(obj) -> bytes:
    url = obj["url"]
    return url
    # TODO dcep93
    # fetch_params = obj["fetch_params"]
    # css_selector = obj["css_selector"]
    # img_data = await asyncio.wait_for(screenshot.screenshot(url, fetch_params, css_selector,), 60.0)
    # return img_data