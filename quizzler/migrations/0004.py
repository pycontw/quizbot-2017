"""Create table to store IM identifications for users.
"""

from quizzler import db


previous = '0003'


def forward():
    c = db.get_cursor()
    c.execute("""
        CREATE TABLE "user_im" (
            "user_serial" varchar(255) NOT NULL REFERENCES "user" ("serial"),
            "im_type" varchar(255) NOT NULL,
            "im_id" varchar(255) NOT NULL,
            PRIMARY KEY ("im_type", "im_id"))
    """)
