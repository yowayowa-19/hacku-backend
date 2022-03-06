from fastapi import FastAPI
import uvicorn
from libs.db_util import create_database
from libs.register import UserCredential

from libs.register import register_c

app = FastAPI()


@app.post("/akubi")
def akubi():
    return {"message": "hello"}


@app.get("/combo")
def combo():
    return {"combo_count": 0}


@app.post("/register")
def register(user: UserCredential) -> dict[str:str]:
    return register_c(user)
    # return {}

def main():
    create_database()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()