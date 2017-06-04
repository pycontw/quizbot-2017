import atexit

import psycopg2

from .env import DATABASE_INFO


_arg_key_pairs = [
    ('host', 'HOST'),
    ('port', 'PORT'),
    ('user', 'USER'),
    ('password', 'PASSWORD'),
    ('dbname', 'NAME'),
]


def _build_connct_arg():
    return ' '.join(
        f'{arg}={DATABASE_INFO[key]}'
        for arg, key in _arg_key_pairs
        if DATABASE_INFO[key]
    )


_conn = None


def cleanup():
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


def commit():
    if _conn is not None:
        _conn.commit()


def get_cursor():
    global _conn
    if _conn is None:
        arg = _build_connct_arg()
        _conn = psycopg2.connect(arg)
        atexit.register(cleanup)
    return _conn.cursor()
