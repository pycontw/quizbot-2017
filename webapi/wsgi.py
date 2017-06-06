import os
import subprocess
from urllib.request import urlretrieve
from django.core.wsgi import get_wsgi_application
from werkzeug.wsgi import DispatcherMiddleware

from .app import app as flask_app
from .line.app import configure_linebot_app


subprocess.call(['python', '-m', 'quizzler.migrations'])

if not os.path.isfile('sources.zip'):
    urlretrieve(os.environ.get('SOURCES_URL'), filename='sources.zip')

if not os.path.isfile('tickets.zip'):
    urlretrieve(os.environ.get('TICKETS_URL'), filename='tickets.zip')


configure_linebot_app(flask_app)

app = DispatcherMiddleware(flask_app, {
    '/api/fb_webhook': get_wsgi_application(),
})
