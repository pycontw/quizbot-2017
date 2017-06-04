"""Create index on "user"."score" to sort on it for the leaderboard.
"""

from quizzler import db


previous = '0006'


def forward():
    c = db.get_cursor()
    c.execute("""
        CREATE INDEX "user_score_leader_index" ON "user" ("score" DESC)
    """)
