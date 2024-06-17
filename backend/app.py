import threading
import time

from first2know import cron, server

threading.Thread(
    target=cron.loop,
    daemon=True,
).start()

time.sleep(30)

server.init()

app = server.web_app
