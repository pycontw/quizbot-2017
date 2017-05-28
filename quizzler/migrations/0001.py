"""Create user table.
"""

from quizzler import db


previous = None


def forward():
    c = db.get_cursor()
    c.execute("""CREATE TABLE "user" ("serial" varchar(255) NOT NULL)""")
