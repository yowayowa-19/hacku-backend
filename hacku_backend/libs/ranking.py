import psycopg2

from .db_util import connect
from .view import Ranking, TotalRanking


def ranking_c(user_id: int):
    return TotalRanking(
        combo_ranking=get_ranking(user_id, "combo_ranking"),
        distance_ranking=get_ranking(user_id, "distance_ranking"),
    )


def get_ranking(user_id: int, table_name: str) -> list[Ranking]:
    with connect() as conn, conn.cursor() as cur:
        conn: psycopg2.connection
        cur: psycopg2.cursor
        cur.execute(
            f"""
            SELECT user_ids, first_id, end_id, total_combo_count, total_distance, rank
            FROM {table_name}
            ORDER BY combo_count DESC
            """
        )
        result = cur.fetchall()

        return [
            Ranking(
                user_ids=(x := item[0]),
                contain_user_id=(user_id in x),
                first_id=item[1],
                end_id=item[2],
                total_combo_count=item[3],
                total_distance=item[4],
                rank=item[5],
            )
            for item in result
        ]
