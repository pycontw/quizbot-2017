# from django.core.wsgi import get_wsgi_application
from werkzeug.wsgi import DispatcherMiddleware

from .app import app as flask_app
# from .line.app import configure_linebot_app


# configure_linebot_app(flask_app)

app = DispatcherMiddleware(flask_app, {
    # '/api/fb_webhook': get_wsgi_application(),
})
