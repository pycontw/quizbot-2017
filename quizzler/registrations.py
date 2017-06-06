import collections
import csv
import functools
import io
import os
import zipfile

from .env import ROOT_DIR_PATH, TICKETS_URL
from .utils import ensure_file


__all__ = ['get_registration', 'get_registrations']


class Registration:
    """Wrapper to a registration information entry.
    """
    def __init__(self, row):
        self.row = row
        self.uid = row['Id']
        self.email = row['聯絡人 Email']
        self.nickname = row['Nickname (shown on ID card) / 暱稱 (顯示於識別證)']

    def __repr__(self):
        return f'<Registration {self.uid}>'

    def __getitem__(self, key):
        return self.row[key]


def generate_info():
    tickets_archive_path = ROOT_DIR_PATH.joinpath('tickets.zip')
    ensure_file(tickets_archive_path, TICKETS_URL)

    with zipfile.ZipFile(str(tickets_archive_path)) as zf:
        for name in zf.namelist():
            stem, ext = os.path.splitext(name)
            if ext != '.csv':
                continue
            with zf.open(name) as f:
                # Zipfile only opens file in binary mode, but csv only accepts
                # text files, so we need to wrap this.
                # See <https://stackoverflow.com/questions/5627954>.
                textfile = io.TextIOWrapper(f, encoding='utf8', newline='')
                for row in csv.DictReader(textfile):
                    yield Registration(row)


@functools.lru_cache(maxsize=1)
def get_uid_registration_mapping():
    return {info.uid: info for info in generate_info()}


@functools.lru_cache(maxsize=1)
def get_email_registration_mapping():
    registration_mapping = collections.defaultdict(list)
    for info in generate_info():
        key = info.email.strip()
        registration_mapping[key].append(info)
    return registration_mapping


def get_registration(*, serial):
    return get_uid_registration_mapping()[serial]


def get_registrations(*, email):
    return list(get_email_registration_mapping()[email.strip()])
