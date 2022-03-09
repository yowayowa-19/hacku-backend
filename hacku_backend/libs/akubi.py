import datetime

import psycopg2

from .db_util import connect
from .view import Akubi, AkubiResult, AkubiCombo

# controller


def akubi_c(akubi: Akubi):
    return AkubiResult(last_yawned_at=akubi_m(akubi)).dict()


# model


def akubi_m(akubi: Akubi):
    yawned_at = datetime.now()

    with connect() as conn, conn.cursor() as cur:
        conn: psycopg2.connection
        cur: psycopg2.cursor

        cur.execute(
            """SELECT yawned_at FROM ongoing_combo 
                ORDER BY tmp_id DESC
                LIMIT 1;""",
        )

        last_yawned_at = cur.fetchone()[0]

        if yawned_at - last_yawned_at < datetime.timedelta(minutes=5):

            cur.execute("SELECT * FROM ongoing_combo;")

            ongoing_yawn = cur.fetchall()

            cur.execute(
                """INSERT INTO ongoing_combo (user_id, yawned_at, latitude, longitude) 
                    VALUES(%s, %s, %s, %s) 
                    RETURNING yawned_at;""",
                (akubi.user_id, yawned_at, akubi.latitude, akubi.longitude),
            )

            last_yawned_at = cur.fetchone()[0]

            result = AkubiCombo
            return 
