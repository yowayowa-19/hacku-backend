from datetime import datetime
from typing import Optional

import psycopg2
from pydantic import BaseModel

from libs.db_util import connect

# view

class Akubi(BaseModel):
    user_id: int
    yawned_at: Optional[datetime] # サーバーで生成するから不要
    latitude: float
    longitude: float


# controller

def akubi_c(akubi: Akubi):
    return {"last_yarwned_at": akubi_m(akubi)}

# model

def akubi_m(akubi: Akubi):
    yawned_at = datetime.now()
    
    with connect() as conn, conn.cursor() as cur:
        conn: psycopg2.connection
        cur: psycopg2.cursor
        cur.execute(
            """INSERT INTO akubi (user_id, yawned_at, latitude, longitude) 
                VALUES(%s, %s, %s, %s) 
                RETURNING yawned_at;""",
            (akubi.user_id, yawned_at, akubi.latitude, akubi.longitude),
        )
        return cur.fetchone()[0]
