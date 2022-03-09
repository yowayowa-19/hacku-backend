from datetime import datetime, timedelta

import psycopg2

from .db_util import connect
from .view import Akubi, AkubiCombo

# controller


def akubi_c(akubi: Akubi):
    return akubi_m(akubi).dict()


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

        if yawned_at - last_yawned_at < timedelta(minutes=5):
            cur.execute(
                """DELETE * 
                FROM ongoing_combo 
                RETURNING user_id, yawned_at, latitude, longitude;"""
            )
            cur.executemany(
                """INSERT INTO akubi (user_id, yawned_at, latitude, longitude) 
                VALUES(%s, %s, %s, %s);""",
                (cur.fetchall()),
            )
        cur.execute("SELECT * FROM ongoing_combo;")

        ongoing_yawn = cur.fetchall()

        cur.execute(
            """INSERT INTO ongoing_combo (user_id, yawned_at, latitude, longitude) 
                VALUES(%s, %s, %s, %s) 
                RETURNING yawned_at;""",
            (akubi.user_id, yawned_at, akubi.latitude, akubi.longitude),
        )

        last_yawned_at = cur.fetchone()[0]

        result = AkubiCombo(
            user_id=akubi.user_id,
            combo_count=len(ongoing_yawn) + 1,
            akubis=[
                Akubi(
                    user_id=item[0],
                    yawned_at=item[1],
                    latitude=item[2],
                    longitude=item[3],
                )
                for item in ongoing_yawn
            ],
            last_yawned_at=last_yawned_at,
        )
        return result
