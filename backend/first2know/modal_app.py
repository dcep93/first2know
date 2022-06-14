import cron
import server

@cron.modal_app.asgi()
def app():
    return server.web_app
