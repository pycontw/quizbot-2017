"""Create table to store question sessions for IM accounts.
"""

from quizzler import db


previous = '0004'


def forward():
    c = db.get_cursor()
    c.execute("""
        CREATE TABLE "question_session" (
            "question_id" varchar(255) NOT NULL,
            "im_type" varchar(255) NOT NULL,
            "im_id" varchar(255) NOT NULL,
            PRIMARY KEY ("im_type", "im_id"))
    """)
