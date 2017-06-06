import logging
import shutil

import requests

from .env import DATA_FILE_INFO


__all__ = ['ensure_data_file']


logger = logging.getLogger(__name__)


def ensure_data_file(path, download_url):
    if path.exists():
        return
    logger.info(f'Populating {path} with {download_url}')
    response = requests.get(
        download_url,
        auth=DATA_FILE_INFO['BASIC_AUTH'],
        stream=True,
    )
    response.raw.decode_content = True  # Decompress GZipped response.
    with path.open('wb') as f:
        shutil.copyfileobj(response.raw, f)
