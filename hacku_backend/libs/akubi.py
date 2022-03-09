from datetime import datetime, timedelta

import psycopg2
from geopy.distance import geodesic

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


def decide_combo(cur: psycopg2.cursor):
    cur.execute(
        """DELETE * 
        FROM ongoing_combo 
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




def distance(first: tuple[float], second: tuple[float]) -> float:
    return geodesic(first, second).km


def calc_distance(latlong_list: list[tuple[float]]) -> float:
    result = 0
    [
        result := result + distance(f, s)
        for f, s in zip(latlong_list[:-1], latlong_list[1:])
    ]
    return result

def get_minimal_combo(cur: psycopg2.cursor) -> int:
    cur.execute(
        """SELECT MIN(total_combo_count) FROM combo_ranking;"""
    )
    return cur.fetchone()[0]

def get_minimal_distance(cur: psycopg2.cursor) -> float:
    cur.execute(
        """SELECT MIN(total_distance) FROM distance_ranking;"""
    )
    return cur.fetchone()[0]