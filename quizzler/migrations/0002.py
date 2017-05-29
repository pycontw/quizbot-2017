"""Create answer_history table that saves answering logs of users.

The user table gains a pk on "serial" (for foreign key purpose).
"""

from quizzler import db


previous = '0001'


def forward():
    c = db.get_cursor()
    c.execute("""
        ALTER TABLE "user" ADD PRIMARY KEY ("serial")
    """)
    c.execute("""
        CREATE TABLE "answer_history" (
            "user_serial" varchar(255) NOT NULL REFERENCES "user" ("serial"),
            "question_id" varchar(255) NOT NULL,
            "correctness" bool NOT NULL,
            "created_at" date NOT NULL DEFAULT CURRENT_TIMESTAMP)
    """)
