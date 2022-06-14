import cron
import server

modal_app = cron.modal_app
web_app = server.web_app

@modal_app.asgi()
def app():
    return web_app
