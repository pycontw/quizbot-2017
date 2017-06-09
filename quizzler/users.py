import collections
import functools
import random

from . import db, questions, registrations


__all__ = ['get_user', 'UserDoesNotExist']


def question_id_pair_sort_key(pair, *, correct_counts, total_counts):
    question_id, question = pair
    return (
        correct_counts[question_id],    # Answered correctly the least time.
        total_counts[question_id],      # Answered the least time.
        random.random(),                # Randomly choose one.
    )


HALL_OF_FAME = {
    '32245586',
    '32245816',
    '32416339',
    '32247028',
}


class User:
    """A user is mapped to a regstration serial on KKTIX.

    Every user can be logged in on multiple IM accounts. Answers from all
    accounts are saved to the same user.
    """
    def __init__(self, *, serial):
        self.serial = serial

    def is_hall_of_famer(self):
        return (self.serial in HALL_OF_FAME)

    def get_current_score(self):
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT "score" FROM "user"
            WHERE "serial" = %(user_serial)s
            LIMIT 1
            """,
            {'user_serial': self.serial},
        )
        score, = cursor.fetchone()
        return score

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

        _, best_question = min(
            questions.get_id_question_pairs(),
            key=functools.partial(
                question_id_pair_sort_key,
                correct_counts=correct_counts,
                total_counts=total_counts,
            ),
        )
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


def add_user_im(*, serial, im_type, im_id):
    """Create a new entry for given serial.

    This function DOES NOT check whether the serial is valid (you must use
    ``quizzler.registrations.get_registrations`` to check), and assumes an
    existing IM identification has not been used. Returns a `User` under
    which the identification is registered.
    """
    cursor = db.get_cursor()
    cursor.execute(
        """
        SELECT EXISTS(
            SELECT * FROM "user"
            WHERE "serial" = %(user_serial)s
        )
        """,
        {'user_serial': serial},
    )
    has_user, = cursor.fetchone()
    if not has_user:
        cursor.execute(
            """
            INSERT INTO "user" ("serial")
            VALUES (%(user_serial)s)
            """,
            {'user_serial': serial},
        )
    cursor.execute(
        """
        INSERT INTO "user_im" ("user_serial", "im_type", "im_id")
        VALUES (%(user_serial)s, %(im_type)s, %(im_id)s)
        """,
        {
            'user_serial': serial,
            'im_type': im_type,
            'im_id': im_id,
        },
    )
    return User(serial=serial)


def remove_user_im(*, im_type, im_id):
    """Remove corresponding IM entry.

    This function only disconnect the given IM account to the user, but
    DOES NOT remove the user itself. Returns the count of entries deleted.
    """
    cursor = db.get_cursor()
    cursor.execute(
        """
        DELETE FROM "user_im"
        WHERE "im_type" = %(im_type)s AND "im_id" = %(im_id)s
        """,
        {
            'im_type': im_type,
            'im_id': im_id,
        },
    )
    count = cursor.rowcount
    return count


Leader = collections.namedtuple('Leader', 'ranking score user registration')


def generate_leaders(*, leader_factory=None):
    """Creates a generator for the leaderboard.

    Generates a 4-tuple containing the ranking, score, user object, and
    registration information of the leader. The result is a namedtuple.
    """
    if leader_factory is None:
        leader_factory = Leader
    cursor = db.get_cursor()
    cursor.execute("""
        SELECT "serial", "score"
        FROM "user"
        ORDER BY "score" DESC
    """)

    ranking_counter = 1
    for serial, score in cursor:
        user = User(serial=serial)
        registration = registrations.get_registration(serial=serial)
        if user.is_hall_of_famer():
            ranking = None
        else:
            ranking = ranking_counter
            ranking_counter += 1
        yield leader_factory(
            ranking=ranking, score=score,
            user=user, registration=registration,
        )
