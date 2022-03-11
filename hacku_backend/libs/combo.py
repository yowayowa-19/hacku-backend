import psycopg2


from .db_util import connect
from .util import calc_distance
from .view import Akubi, AkubiCombo, LastAkubi

# controller


def combo_c(last_akubi: LastAkubi):
    akubis = combo_m(last_akubi)

    # print(f'{last_akubi=}')
    # print(f"combo(l14): {akubis=}")


    # コンボ終了！
    if len(akubis) == 0:
        return AkubiCombo(
            user_id=last_akubi.user_id,
            combo_count=0,
            distance=0,
            akubis=[],
            last_yawned_at=last_akubi.last_yawned_at,
        ).dict()

    # コンボ継続中！
    last_latlong = get_last_latlong()
    latlong_list = [(last_latlong[0], last_latlong[1])] + [
        (akubi[2], akubi[3]) for akubi in akubis
    ]
    print(f'(l33) {latlong_list=}')
    return AkubiCombo(
        user_id=last_akubi.user_id,
        combo_count=len(akubis),
        distance=calc_distance(latlong_list),
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
    with connect() as conn, conn.cursor() as cur:
        conn: psycopg2.connection
        cur: psycopg2.cursor
        cur.execute(
            """
            SELECT user_id, yawned_at, latitude, longitude
            FROM ongoing_combo 
            WHERE %s < yawned_at;
            """,
            (last_akubi.last_yawned_at,),
        )
        result = cur.fetchall()
        return result


def get_last_latlong():
    with connect() as conn, conn.cursor() as cur:
        conn: psycopg2.connection
        cur: psycopg2.cursor
        # コンボ継続中だったらakubiはだめ．ongoing_comboから取ってくる．
        cur.execute(
            """
            SELECT latitude, longitude
            FROM ongoing_combo
            ORDER BY yawned_at DESC
            LIMIT 1;
            """,
        )
        result = cur.fetchone()
        return result
