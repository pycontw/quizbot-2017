"""Create table to store generic conversation states for IM accounts.

This replaces the "question_session" table introduced in 0005.
"""

import json

import psycopg2.extras

from quizzler import db, im


previous = '0005'


def make_question_state_row(question_id, im_type, im_id):
    return (
        im_type,
        im_id,
        im.ConversationState.question.value,
        json.dumps({'question_id': question_id}),
    )


def forward():
    c = db.get_cursor()
    c.execute("""
        CREATE TABLE "im_conversation_state" (
            "im_type" varchar(255) NOT NULL,
            "im_id" varchar(255) NOT NULL,
            "state" integer NOT NULL,
            "extra" text NOT NULL DEFAULT '',
            PRIMARY KEY ("im_type", "im_id", "state"))
    """)

    # Migrate old data.
    c.execute("""
        SELECT "question_id", "im_type", "im_id" FROM "question_session"
    """)
    psycopg2.extras.execute_values(
        c,
        """
        INSERT INTO "im_conversation_state" (
            "im_type", "im_id", "state", "extra") VALUES %s
        """,
        [make_question_state_row(*row) for row in c],
    )

    c.execute("""
        DROP TABLE IF EXISTS "question_session"
    """)
