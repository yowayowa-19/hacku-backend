import base64
import hashlib
import os

from pydantic import BaseModel

from .db_util import connect

import psycopg2

# view
class UserCredential(BaseModel):
    name: str
    password: str

class UserId(BaseModel):
    id: int

# controller


def register_c(user: UserCredential) -> dict[str: int]:
    return {"id": create_user(user)}


# model
def register_m():
    pass


def create_user(user: UserCredential) -> int:
    salt = base64.b64encode(os.urandom(32))
    b_password = bytes(user.password, encoding="utf-8")
    digest = hashlib.sha512(salt + b_password).hexdigest()

    with connect() as conn, conn.cursor() as cur:
        conn: psycopg2.connection
        cur: psycopg2.cursor
        cur.execute(
            "INSERT INTO users (name, salt, digest) VALUES(%s, %s, %s) RETURNING id;",
            (user.name, salt, digest),
        )
        return cur.fetchone()[0]
