import threading
import time

from first2know import cron, server


def start_server():
    time.sleep(120)
    server.init()
    cron.loop_with_manager(server.Vars.screenshot_manager)


threading.Thread(
    target=start_server,
    daemon=True,
).start()

app = server.web_app
