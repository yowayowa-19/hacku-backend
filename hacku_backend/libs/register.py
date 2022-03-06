import base64
import hashlib
import os

from pydantic import BaseModel

from .db_util import connect


# view
class UserCredential(BaseModel):
    name: str
    password: str


# controller

def register_c(user: UserCredential) -> dict[str:str]:
    create_user(user)
    return {"message": "connected"}

# model
def register_m():
    pass

def create_user(user: UserCredential):
    salt = base64.b64encode(os.urandom(32))
    b_password = bytes(user.password, encoding="utf-8")
    digest = hashlib.sha512(salt + b_password).hexdigest()
    
    conn = connect()
    cur = conn.cursor()
    cur.execute('INSERT INTO users (name, salt, digest) VALUES(%s, %s, %s);', (user.name, salt, digest))
    pass
