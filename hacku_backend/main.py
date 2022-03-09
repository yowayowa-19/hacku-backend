import uvicorn
from fastapi import FastAPI

from libs.akubi import Akubi, AkubiResult, akubi_c
from libs.combo import AkubiCombo, LastAkubi, combo_c
from libs.db_util import create_database
from libs.register import UserCredential, UserId, register_c

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


def main():
    create_database()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
