import psycopg2


from .db_util import connect
from .view import Akubi, AkubiCombo, LastAkubi

# controller


def combo_c(last_akubi: LastAkubi):
    akubis = combo_m(last_akubi)
    if len(akubis) == 0:
        return AkubiCombo(
            user_id=last_akubi.user_id,
            combo_count=0,
            akubis=[],
            last_yawned_at=last_akubi.last_yawned_at,
        ).dict()
    return AkubiCombo(
        user_id=last_akubi.user_id,
        combo_count=len(akubis),
        akubis=[
            Akubi(
                user_id=item[0],
                yawned_at=item[1],
                latitude=item[2],
                longitude=item[3],
            )
            for item in akubis
        ],
        last_yawned_at=akubis[-1][1],
    ).dict()


# model
def combo_m(last_akubi: LastAkubi):
    combo_acceptance_time = 5
    with connect() as conn, conn.cursor() as cur:
        conn: psycopg2.connection
        cur: psycopg2.cursor
        cur.execute(
            """
            SELECT user_id, yawned_at, latitude, longitude
            FROM ongoing_combo 
            WHERE yawned_at < %s
            AND %s < yawned_at + cast( '%s minutes' as interval);
            """,
            (
                last_akubi.last_yawned_at,
                last_akubi.last_yawned_at,
                combo_acceptance_time,
            ),
        )
        result = cur.fetchall()
        # print(result)
        return result

