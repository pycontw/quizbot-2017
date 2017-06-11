from . import db


__all__ = ['generate_bot_serials']


def generate_bot_serials():
    """Observe the log to detect non-human clients.

    The logic is to take 5-minute intervals, and if a user answers
    150 questions or more in that period (2 seconds per question),
    it is probably too quick.
    """
    cursor = db.get_cursor()
    cursor.execute(
        """
        SELECT DISTINCT "user"."serial" FROM "user"
        INNER JOIN (
            SELECT
                "user_serial",
                (extract(minute FROM "created_at")::int / 5) AS "slot"
            FROM "answer_history"
            WHERE "created_at" != '2017-06-09 00:00:00'
            GROUP BY "user_serial", "slot"
            HAVING COUNT(*) > %(bot_like_threshold)s
        ) AS "period_over_count"
        ON ("period_over_count"."user_serial" = "user"."serial")
        GROUP BY "user"."serial"
        HAVING COUNT(*) > %(allowed_violation_count)s
        """,
        {'bot_like_threshold': 50, 'allowed_violation_count': 3},
    )
    for serial, in cursor:
        yield serial
