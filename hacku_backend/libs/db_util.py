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
    return conn


def connect_delay():
    conn = None
    while not conn:
        conn = connect()
    return conn



def create_database():
    with conn := connect_delay(), cur := conn.cursor():
        cur.execute(
            """CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                name TEXT, 
                salt TEXT, 
                digest TEXT);"""
        )
        
        cur.execute(
            """CREATE TABLE IF NOT EXISTS akubi (
                akubi_id SERIAL PRIMARY KEY,
                user_id INTEGER,
                yawned_at TIMESTAMP,
                latitude REAL,
                longitude REAL,
            )"""
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS akubi_combo(
                combo_id SERIAL PRIMARY KEY,
                combo_count INTEGER,
                distance REAL,
            )"""
        )

        conn.commit()

        