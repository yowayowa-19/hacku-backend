import psycopg2

from .db_util import connect
from .view import Ranking, TotalRanking


def ranking_c(user_id: int):
    return TotalRanking(
        combo_ranking=get_ranking(user_id, "combo_ranking", "total_combo_count"),
        distance_ranking=get_ranking(user_id, "distance_ranking", "total_distance"),
    )


def get_ranking(user_id: int, table_name: str, order_column: str) -> list[Ranking]:
    with connect() as conn, conn.cursor() as cur:
        conn: psycopg2.connection
        cur: psycopg2.cursor
        cur.execute(
            f"""
            SELECT user_ids, first_id, users.name, end_id, total_combo_count, total_distance, ranking 
            FROM {table_name} INNER JOIN users ON {table_name}.first_id = users.user_id
            ORDER BY {order_column} DESC
            """
        )
        result = cur.fetchall()

        return [
            Ranking(
                user_ids=(x := item[0]),
                contain_user_id=(user_id in x),
                first_id=item[1],
                first_id_name=item[2],
                end_id=item[3],
                total_combo_count=item[4],
                total_distance=item[5],
                rank=item[6],
            )
            for item in result
        ]
