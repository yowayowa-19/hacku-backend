import time

import psycopg2


def connect():
    # TODO read from config
    username = "yowayowa"
    password = "pass"
    hostname = "postgres"
    port = 5432
    database = "pg"

    try:
        conn = psycopg2.connect(
            f"postgresql://{username}:{password}@{hostname}:{port}/{database}"
        )
    except Exception as e:
        print("I am unable to connect to the database")
        print(e)
        time.sleep(5)
        return None

    print(type(conn))
    return conn


def connect_delay():
    conn = None
    while not conn:
        conn = connect()
    return conn


def create_database():

    with connect_delay() as conn, conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT, 
                salt TEXT, 
                digest TEXT);"""
        )
        conn.commit()
