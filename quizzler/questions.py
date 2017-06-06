import functools
import os
import textwrap
import zipfile

import yaml

from .env import ROOT_DIR_PATH, DATA_FILE_INFO
from .utils import ensure_data_file


class Question:
    """A question to answer!
    """
    def __init__(self, uid, entry):
        self.uid = uid
        self.message = entry['question']
        self.answer = entry['answer']
        self.wrong_choices = entry['wrong_choices']

    def __repr__(self):
        message_snippet = textwrap.shorten(self.message, width=30)
        return f'<Question {self.uid} {message_snippet!r}>'

    def get_score(self, correctness):
        if correctness:
            return 1 + len(self.wrong_choices)
        return 1


def generate_question_in_source(name, f):
    for entry in yaml.load(f):
        uid = f'{name}-{entry["id"]}'
        yield uid, Question(uid, entry)


def generate_question():
    sources_archive_path = ROOT_DIR_PATH.joinpath('sources.zip')
    ensure_data_file(sources_archive_path, DATA_FILE_INFO['SOURCES_URL'])

    with zipfile.ZipFile(str(sources_archive_path)) as zf:
        for name in zf.namelist():
            stem, ext = os.path.splitext(os.path.basename(name))
            if ext != '.yml':
                continue
            with zf.open(name) as f:
                yield from generate_question_in_source(stem, f)


@functools.lru_cache(maxsize=1)
def get_id_question_pairs():
    return list(generate_question())


@functools.lru_cache(maxsize=1)
def get_question_mapping():
    pairs = get_id_question_pairs()
    mapping = dict(pairs)
    assert len(mapping) == len(pairs)   # No duplicate entries.
    return mapping


def get_question(question_id):
    return get_question_mapping()[question_id]
