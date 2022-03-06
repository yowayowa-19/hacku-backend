from datetime import datetime
from pydantic import BaseModel

from hacku_backend.libs.db_util import connect

# view

class Akubi(BaseModel):
    user_id: int
    # yawned_at: datetime サーバーで生成するから不要
    latitude: float
    longitude: float


# controller

def akubi_c(akubi: Akubi):
    akubi_m(akubi)
    return {"message": "ok"}

# model

def akubi_m(akubi: Akubi):
    yawned_at = datetime.now()
    
    with conn := connect(), cur := conn.cursor():
        cur.execute(
            """INSERT INTO akubi (user_id, yawned_at, latitude, longitude) 
                VALUES(%d, %s, %lf, %lf);""",
            (akubi.user_id, yawned_at, akubi.latitude, akubi.longitude),
        )
        # return cur.fetchone()[0]