import threading
import uvicorn

from .first2know import cron, server

threading.Thread(
    target=lambda: uvicorn.run(server.web_app, host="0.0.0.0", port=8000),
    daemon=True,
).start()


def setState(state):
    server.Vars.state = state


cron.loop(setState)
raise Exception("loop_finished")
