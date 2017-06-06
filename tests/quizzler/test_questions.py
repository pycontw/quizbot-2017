from quizzler import questions


def test_load():
    """Make sure the files load, and there's no duplicate entries.
    """
    pairs = questions.get_id_question_pairs()
    mapping = questions.get_question_mapping()
    assert len(mapping) == len(pairs)
