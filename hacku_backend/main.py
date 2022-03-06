import uvicorn
from fastapi import FastAPI

from libs.akubi import Akubi, akubi_c
from libs.combo import LastAkubi, combo_c
from libs.db_util import create_database
from libs.register import UserCredential, register_c

app = FastAPI()


@app.post("/akubi")
def akubi(akubi: Akubi):
    "yawned_atはいらないです"
    return akubi_c(akubi)


@app.post("/combo")
def combo(last_akubi: LastAkubi):
    return combo_c(last_akubi)
    # return {"combo_count": 0}


@app.post("/register")
def register(user: UserCredential) -> dict[str:str]:
    return register_c(user)
    # return {}


def main():
    create_database()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
