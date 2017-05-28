import random

from . import questions


class User:
    """A user is mapped to a regstration serial on KKTIX.

    Every user can be logged in on multiple IM accounts. Answers from all
    accounts are saved to the same user.
    """
    def __init__(self, serial):
        self.serial = serial

    def get_next_question(self):
        # TODO: Implement the *real* question-selection algorithm.
        # This just returns a random qustion for now.
        pairs = questions.get_id_question_pairs()
        return pairs[random.randint(0, len(pairs) - 1)][-1]
