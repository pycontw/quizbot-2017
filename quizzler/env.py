import os
import pathlib

import dj_database_url
import dotenv


__all__ = ['ROOT_DIR_PATH', 'DATABASE_INFO', 'SOURCES_URL', 'TICKETS_URL']


ROOT_DIR_PATH = pathlib.Path(__file__).resolve().parent.parent

dotenv.load_dotenv(str(ROOT_DIR_PATH.joinpath('.env')))


DATABASE_INFO = dj_database_url.parse(os.environ['DATABASE_URL'])

SOURCES_URL = os.environ.get('SOURCES_URL', '')

TICKETS_URL = os.environ.get('TICKETS_URL', '')

# This logs everything to stderr.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {    # Match access log style.
            'format': '[%(asctime)s] "%(levelname)s %(name)s" %(message)s',
            'datefmt': r'%d/%b/%Y %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 0,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'root': {
        'level': 0,
        'handlers': ['console'],
    }
}
