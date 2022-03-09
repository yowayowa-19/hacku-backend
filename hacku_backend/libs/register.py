import base64
import hashlib
import os

from .db_util import connect
from .view import UserCredential


import psycopg2

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
            "INSERT INTO users (name, salt, digest) VALUES(%s, %s, %s) RETURNING user_id;",
            (user.name, salt, digest),
        )
        return cur.fetchone()[0]
