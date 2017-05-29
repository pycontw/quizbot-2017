"""Create column on the user table to save the user's score.
"""

from quizzler import db


previous = '0002'


def forward():
    c = db.get_cursor()
    c.execute("""
        ALTER TABLE "user" ADD COLUMN "score" integer NOT NULL DEFAULT 0
    """)
