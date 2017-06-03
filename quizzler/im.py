import enum
import json

from . import db, questions


__all__ = [
    'ConversationState',

    'get_current_question', 'set_current_question',

    'is_registration_session_active', 'activate_registration_session',
    'complete_registration_session',

    'NoConversationStateMatch', 'CurrentQuestionDoesNotExist',
    'RegistrationSessionNotActive',
]


class ConversationState(enum.IntEnum):
    registration = 0
    question = 1


class NoConversationStateMatch(ValueError):
    """Common error class for an invalid state request.
    """
    def __init__(self, *, im_type, im_id):
        super().__init__(f'(type={im_type!r}, id={im_id!r})')


def set_state(*, im_type, im_id, state, extra):
    cursor = db.get_cursor()
    cursor.execute(
        """
        INSERT INTO "im_conversation_state" (
            "im_type", "im_id", "state", "extra")
        VALUES (%(im_type)s, %(im_id)s, %(state)s, %(extra)s)
        """,
        {
            'im_type': im_type,
            'im_id': im_id,
            'state': state,
            'extra': json.dumps(extra),
        },
    )


def clear_state(*, im_type, im_id, state):
    cursor = db.get_cursor()
    cursor.execute(
        """
        DELETE FROM "im_conversation_state"
        WHERE "im_type" = %(im_type)s
          AND "im_id" = %(im_id)s
          AND "state" = %(state)s
        """,
        {'im_type': im_type, 'im_id': im_id, 'state': state},
    )


class CurrentQuestionDoesNotExist(NoConversationStateMatch):
    pass


def get_current_question(*, im_type, im_id):
    """Get the question this IM account is currently answering.

    `CurrentQuestionDoesNotExist` is raised if there's no active question
    waiting for answer.
    """
    cursor = db.get_cursor()
    cursor.execute(
        """
        SELECT "extra" FROM "im_conversation_state"
        WHERE "im_type" = %(im_type)s
          AND "im_id"   = %(im_id)s
          AND "state"   = %(state)s
        LIMIT 1
        """,
        {
            'im_type': im_type,
            'im_id': im_id,
            'state': ConversationState.question.value,
        },
    )
    row = cursor.fetchone()
    if row is None:
        raise CurrentQuestionDoesNotExist(im_type=im_type, im_id=im_id)
    extra, = row
    question_id = json.loads(extra)['question_id']
    return questions.get_question(question_id)


def set_current_question(*, question, im_type, im_id):
    """Set the current question.

    The `question` argument can be `None`.
    """
    clear_state(
        im_type=im_type, im_id=im_id,
        state=ConversationState.question.value,
    )
    if question is not None:
        set_state(
            im_type=im_type, im_id=im_id,
            state=ConversationState.question.value,
            extra={'question_id': question.uid},
        )


class RegistrationSessionNotActive(NoConversationStateMatch):
    pass


def is_registration_session_active(*, im_type, im_id):
    """Check whether this user has an active registration session.
    """
    cursor = db.get_cursor()
    cursor.execute(
        """
        SELECT EXISTS(
            SELECT * FROM "im_conversation_state"
            WHERE "im_type" = %(im_type)s
              AND "im_id"   = %(im_id)s
              AND "state"   = %(state)s
            LIMIT 1
        )
        """,
        {
            'im_type': im_type,
            'im_id': im_id,
            'state': ConversationState.registration.value,
        },
    )
    activeness, = cursor.fetchone()
    return activeness


def activate_registration_session(*, im_type, im_id):
    set_state(
        im_type=im_type, im_id=im_id,
        state=ConversationState.registration.value,
        extra=None,
    )


def complete_registration_session(*, im_type, im_id):
    clear_state(
        im_type=im_type, im_id=im_id,
        state=ConversationState.registration.value,
    )
