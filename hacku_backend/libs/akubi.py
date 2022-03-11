import random
from datetime import datetime, timedelta

import psycopg2

from .db_util import connect
from .util import calc_distance, distance
from .view import Akubi, AkubiCombo

# controller


def akubi_c(akubi: Akubi):
    return akubi_m(akubi).dict()


# model


def akubi_m(akubi: Akubi):
    yawned_at = datetime.now()

    # 5kmの円の中くらいでずらしたい

    noized_latitude = akubi.latitude + random.uniform(-0.04, 0.04)
    noized_longitude = akubi.longitude + random.uniform(-0.04, 0.04)

    with connect() as conn, conn.cursor() as cur:
        conn: psycopg2.connection
        cur: psycopg2.cursor

        # 現在継続中のコンボのうち，最後のレコードの時刻を取得
        cur.execute(
            """SELECT yawned_at FROM ongoing_combo 
                ORDER BY tmp_id DESC
                LIMIT 1;""",
        )

        last_yawned_at = cur.fetchone()[0] if cur.rowcount > 0 else None
        print(f'{last_yawned_at=}')

        # コンボが継続中で，最後のレコードの時刻から5s(m)たっていたら，コンボを終了する
        # コンボが終了したら，継続コンボテーブルを削除して，削除したものをあくび表に挿入
        if last_yawned_at and yawned_at - last_yawned_at > timedelta(minutes=5):
            cur.execute(
                """DELETE FROM ongoing_combo 
                RETURNING user_id, yawned_at, latitude, longitude;"""
            )
            result = cur.fetchall()
            print(f'コンボ終了時に走る処理{result=}')
            cur.executemany(
                """INSERT INTO akubi (user_id, yawned_at, latitude, longitude) 
                VALUES(%s, %s, %s, %s);""",
                (result),
            )

        # 継続コンボテーブルからデータを持ってくる．
        # データがあるなら，コンボが継続中ということである．
        cur.execute("SELECT * FROM ongoing_combo;")
        ongoing_yawn = cur.fetchall()

        cur.execute(
            """INSERT INTO ongoing_combo (user_id, yawned_at, latitude, longitude) 
                VALUES(%s, %s, %s, %s) 
                RETURNING yawned_at;""",
            (akubi.user_id, yawned_at, noized_latitude, noized_longitude),
        )

        last_yawned_at = cur.fetchone()[0]

        if len(ongoing_yawn) == 0:
            distance = 0
        else:
            distance = calc_distance([(item[3], item[4]) for item in ongoing_yawn])

        print(f'{ongoing_yawn=}')

        result = AkubiCombo(
            user_id=akubi.user_id,
            combo_count=len(ongoing_yawn) + 1,
            distance=distance,
            akubis=[
                Akubi(
                    user_id=item[1],
                    yawned_at=item[2],
                    latitude=item[3],
                    longitude=item[4],
                )
                for item in ongoing_yawn
            ],
            last_yawned_at=last_yawned_at,
        )
        return result


def decide_combo(cur):
    cur: psycopg2.cursor
    cur.execute(
        """DELETE FROM ongoing_combo 
        RETURNING user_id, yawned_at, latitude, longitude;"""
    )

    result = cur.fetchall()
    cur.executemany(
        """INSERT INTO akubi (user_id, yawned_at, latitude, longitude) 
        VALUES(%s, %s, %s, %s);""",
        (result),
    )

    latlong_list = [(item[2], item[3]) for item in result]

    use_ids = [item[0] for item in result]
    first_id = use_ids[0]
    end_id = use_ids[-1]
    total_combo_count = len(result)
    total_distance = calc_distance(latlong_list)

    minimal_combo = get_minimal_combo(cur)
    minimal_distance = get_minimal_distance(cur)

    if minimal_combo <= total_combo_count:
        cur.execute(
            """INSERT INTO combo_ranking (user_ids, first_id, end_id, total_combo_count, total_distance) 
            VALUES(%s, %s, %s, %s, %s); """
        )
        cur.execute(
            """UPDATE combo_ranking
            SET ranking = r.rnk
            FROM (rank_id, RANK() OVER (ORDER BY total_combo_count) AS rnk) r
            WHERE combo_ranking.rank_id = r.rank_id;"""
        )
        cur.execute(
            """DELETE FROM combo_ranking
                WHERE ranking > 10;"""
        )

    if minimal_distance <= total_distance:
        cur.execute(
            """INSERT INTO distance_ranking (user_ids, first_id, end_id, total_combo_count, total_distance) 
            VALUES(%s, %s, %s, %s, %s); """
        )
        cur.execute(
            """UPDATE distance_ranking
            SET ranking = r.rnk
            FROM (rank_id, RANK() OVER (ORDER BY total_distance) AS rnk) r
            WHERE distance_ranking.rank_id = r.rank_id;"""
        )
        cur.execute(
            """DELETE FROM distance_ranking
                WHERE ranking > 10;"""
        )

    cur.execute(
        """ 
        SELECT total_combo_count 
        FROM combo_ranking
        ORDER BY total_combo_count DESC
        """
    )

    cur.execute(
        """INSERT INTO combo_ranking (
            user_ids, first_id, end_id, total_combo_count, total_distance);""",
        (use_ids, first_id, end_id, total_combo_count, total_distance),
    )


def get_minimal_combo(cur) -> int:
    cur: psycopg2.cursor
    cur.execute("""SELECT MIN(total_combo_count) FROM combo_ranking;""")
    return cur.fetchone()[0]


def get_minimal_distance(cur) -> float:
    cur: psycopg2.cursor
    cur.execute("""SELECT MIN(total_distance) FROM distance_ranking;""")
    return cur.fetchone()[0]
