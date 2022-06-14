import asyncio
import time

import modal

from ...backend.first2know import screenshot # pylint: disable=relative-beyond-top-level

stub = modal.Stub()

@stub.function(schedule=modal.Period(minutes=1))
async def run_cron():
    print("run_cron")
    print(time.time())
    url = "https://chess.com"
    img_data = await asyncio.wait_for(screenshot.screenshot(url), 60.0)
    print(len(img_data))
    print("done")