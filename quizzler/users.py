import collections
import functools
import random

from . import db, questions


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
    def __init__(self, serial):
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
