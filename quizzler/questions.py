import functools
import os
import textwrap
import zipfile

import yaml

from .env import ROOT_DIR_PATH


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
    for i, entry in enumerate(yaml.load(f)):
        # TODO: Mayebe implement a better UID?
        uid = f'{name}-{i}'
        yield uid, Question(uid, entry)


def generate_question():
    with zipfile.ZipFile(str(ROOT_DIR_PATH.joinpath('sources.zip'))) as zf:
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
def get_question_map():
    return dict(get_id_question_pairs())


def get_question(question_id):
    return get_question_map()[question_id]
