"""Record date *and* time on "answer_history"."created_at".
"""

from quizzler import db


previous = '0007'


def forward():
    c = db.get_cursor()
    c.execute("""
        ALTER TABLE "answer_history" ALTER COLUMN "created_at" TYPE timestamp
    """)
