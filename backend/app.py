import threading
import uvicorn

raise Exception("checking")



from .first2know import cron, server

threading.Thread(
    target=lambda: uvicorn.run(server.web_app, host="0.0.0.0", port=8000),
    daemon=True,
).start()
cron.loop()
raise Exception("loop_finished")
