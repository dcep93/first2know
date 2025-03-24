import sys
import threading

from first2know import cron, logger, server

logger.log("app.py::init.sys.argv", sys.argv)

server.init()

threading.Thread(
    target=lambda: cron.loop_with_manager(server.Vars.screenshot_manager),
    daemon=True,
).start()

app = server.web_app
