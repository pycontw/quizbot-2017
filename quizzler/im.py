from . import db, questions


__all__ = [
    'get_current_question', 'set_current_question',
    'CurrentQuestionDoesNotExist',
]


class CurrentQuestionDoesNotExist(ValueError):
    def __init__(self, *, im_type, im_id):
        super().__init__(f'(type={im_type!r}, id={im_id!r})')


def get_current_question(*, im_type, im_id):
    """Get the question this IM account is currently answering.

    `CurrentQuestionDoesNotExist` is raised if there's no active question
    waiting for answer.
    """
    cursor = db.get_cursor()
    cursor.execute(
        """
        SELECT "question_id" FROM "question_session"
        WHERE "im_type" = %(im_type)s AND "im_id" = %(im_id)s
        LIMIT 1
        """,
        {'im_type': im_type, 'im_id': im_id},
    )
    row = cursor.fetchone()
    if row is None:
        raise CurrentQuestionDoesNotExist(im_type=im_type, im_id=im_id)
    question_id, = row
    return questions.get_question(question_id)


def set_current_question(*, question, im_type, im_id):
    cursor = db.get_cursor()
    cursor.execute(
        """
        DELETE FROM "question_session"
        WHERE "im_type" = %(im_type)s AND "im_id" = %(im_id)s
        """,
        {'im_type': im_type, 'im_id': im_id},
    )
    cursor.execute(
        """
        INSERT INTO "question_session" (
            "question_id", "im_type", "im_id")
        VALUES (%(question_id)s, %(im_type)s, %(im_id)s)
        """,
        {'question_id': question.uid, 'im_type': im_type, 'im_id': im_id},
    )
