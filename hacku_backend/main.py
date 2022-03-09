import uvicorn
from fastapi import FastAPI

from libs.akubi import akubi_c
from libs.combo import combo_c
from libs.db_util import create_database
from libs.ranking import ranking_c
from libs.register import register_c
from libs.view import *

app = FastAPI()


@app.post("/akubi/", response_model=AkubiCombo)
def akubi(akubi: Akubi):
    "yawned_atはいらないです"
    return akubi_c(akubi)


@app.post("/combo/", response_model=AkubiCombo)
def combo(last_akubi: LastAkubi):
    "検証用にコンボ受付時間を5分に設定しています"
    return combo_c(last_akubi)
    # return {"combo_count": 0}


@app.post("/register/", response_model=UserId)
def register(user: UserCredential) -> dict[str:str]:
    return register_c(user)
    # return {}


@app.get("/ranking", response_model=TotalRanking)
def ranking(user_id: int):

    return ranking_c(user_id)
    # return {}


def main():
    create_database()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
