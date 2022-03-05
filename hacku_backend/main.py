import imp
from fastapi import FastAPI

app = FastAPI()


@app.post("/akubi")
def akubi():
    return {"message": "hello"}


@app.get("/combo")
def combo():
    return {"combo_count": 0}


@app.get("/register")
def register():
    return {}

