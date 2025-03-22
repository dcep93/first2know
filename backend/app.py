import sys
import threading
import time

from first2know import cron, server

print(sys.argv)

server.init()

# threading.Thread(
#     target=lambda: cron.loop_with_manager(server.Vars.screenshot_manager),
#     daemon=True,
# ).start()

app = server.web_app
