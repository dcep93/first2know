import threading

from first2know import cron, server

threading.Thread(
    target=cron.loop,
    daemon=True,
).start()

server.init()

app = server.web_app
