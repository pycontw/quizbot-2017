import collections
import functools
import random

from . import db, questions


__all__ = ['get_user', 'UserDoesNotExist']


def question_id_pair_sort_key(pair, *, correct_counts, total_counts):
    question_id, question = pair
    return (
        correct_counts[question_id],    # Answered correctly the least time.
        total_counts[question_id],      # Answered the least time.
        random.random(),                # Randomly choose one.
    )


class User:
    """A user is mapped to a regstration serial on KKTIX.

    Every user can be logged in on multiple IM accounts. Answers from all
    accounts are saved to the same user.
    """
    def __init__(self, *, serial):
        self.serial = serial

    def get_next_question(self):
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT COUNT(*) AS "count", "question_id", "correctness"
            FROM "answer_history"
            WHERE "user_serial" = %(user_serial)s AND "correctness" = TRUE
            GROUP BY ("question_id", "correctness")
            """,
            {'user_serial': self.serial},
        )
        correct_counts = collections.defaultdict(int)
        total_counts = collections.defaultdict(int)
        for count, question_id, correctness in cursor:
            if correctness:
                correct_counts[question_id] += count
            total_counts[question_id] += count

        candidate_pairs = sorted(
            questions.get_id_question_pairs(),
            key=functools.partial(
                question_id_pair_sort_key,
                correct_counts=correct_counts,
                total_counts=total_counts,
            ),
        )
        best_id, best_question = candidate_pairs[0]
        return best_question

    def save_answer(self, question, correctness):
        cursor = db.get_cursor()
        cursor.execute(
            """
            UPDATE "user"
            SET "score" = "score" + %(score)s
            WHERE "serial" = %(user_serial)s
            """,
            {
                'user_serial': self.serial,
                'score': question.get_score(correctness),
            },
        )
        cursor.execute(
            """
            INSERT INTO "answer_history" (
                "user_serial", "question_id", "correctness")
            VALUES (%(user_serial)s, %(question_id)s, %(correctness)s)
            """,
            {
                'user_serial': self.serial,
                'question_id': question.uid,
                'correctness': correctness,
            },
        )


class UserDoesNotExist(ValueError):
    def __init__(self, *, im_type, im_id):
        super().__init__(f'(type={im_type!r}, id={im_id!r})')


def get_user(*, im_type, im_id):
    """Public API to get user info from provided IM identification.

    Returns a `User` if found, otherwise raises `UserDoesNotExist`.
    """
    cursor = db.get_cursor()
    cursor.execute(
        """
        SELECT "u"."serial" AS "serial" FROM "user" AS "u"
        INNER JOIN "user_im" AS "i" ON ("u"."serial" = "i"."user_serial")
        WHERE "i"."im_type" = %(im_type)s AND "i"."im_id" = %(im_id)s
        LIMIT 1
        """,
        {
            'im_type': im_type,
            'im_id': im_id,
        },
    )
    row = cursor.fetchone()
    if row is None:
        raise UserDoesNotExist(im_type=im_type, im_id=im_id)
    serial, = row
    return User(serial=serial)


def add_user_im(*, ticket, serial, im_type, im_id):
    """Create a new entry for given user serial with given ticket type.

    This function assumes an existing IM identification has not been used.
    Returns a `User` under which the identification is registered.
    """
    serial_with_ticket_type = f'{ticket}-{serial}'
    cursor = db.get_cursor()
    cursor.execute(
        """
        SELECT EXISTS(
            SELECT * FROM "user"
            WHERE "serial" = %(user_serial)s
        )
        """,
        {'user_serial': serial_with_ticket_type},
    )
    has_user, = cursor.fetchone()
    if not has_user:
        cursor.execute(
            """
            INSERT INTO "user" ("serial")
            VALUES (%(user_serial)s)
            """,
            {'user_serial': serial_with_ticket_type},
        )
    cursor.execute(
        """
        INSERT INTO "user_im" ("user_serial", "im_type", "im_id")
        VALUES (%(user_serial)s, %(im_type)s, %(im_id)s)
        """,
        {
            'user_serial': serial_with_ticket_type,
            'im_type': im_type,
            'im_id': im_id,
        },
    )
    return User(serial=serial_with_ticket_type)
