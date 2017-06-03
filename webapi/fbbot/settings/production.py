from .base import *     # noqa


DEBUG = False

ALLOWED_HOSTS = [
    # TODO: Add hosts to whitelist in production.
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {    # Match access log style.
            'format': '%(asctime)s %(levelname).1s [%(name)s] %(message)s',
            'datefmt': r'%d/%b/%Y %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            # TODO: Give me a better configuration.
            'filename': 'facebook-api.log',
            'maxBytes': 1024 * 1024,    # 1 MB.
            'backupCount': 10,
            'formatter': 'default',
        },
    },
    'root': {
        'level': 0,
        'handlers': ['console', 'file'],
    }
}
