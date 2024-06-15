import threading
import uvicorn

from . import cron, server  # type: ignore

raise Exception("checking")
threading.Thread(
    target=lambda: uvicorn.run(server.web_app, host="0.0.0.0", port=8000),
    daemon=True,
).start()
cron.loop()
raise Exception("loop_finished")
