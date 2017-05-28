import os
import pathlib

import dj_database_url
import dotenv


__all__ = ['ROOT_DIR_PATH', 'DATABASE_INFO']


ROOT_DIR_PATH = pathlib.Path(__file__).resolve().parent.parent

dotenv.load_dotenv(str(ROOT_DIR_PATH.joinpath('.env')))

DATABASE_INFO = dj_database_url.parse(os.environ['DATABASE_URL'])
