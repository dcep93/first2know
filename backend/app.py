import uvicorn
import concurrent.futures

from . import cron, server

futures.ThreadPoolExecutor(max_workers=8).submit(
    lambda: uvicorn.run(server.web_app, host="0.0.0.0", port=8000)
)
cron.loop()
raise Exception("loop_finished")
