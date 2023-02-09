#!/usr/bin/env python3

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')


def create_db(db_name, conn_info):
    """Connects to server, creates the database"""
    try:
        conn = psycopg2.connect(
            host=conn_info['host'],
            user=conn_info['user'],
            password=conn_info['password'],
            port=conn_info['port'],
        )
    except Exception as exc:
        print(f"Unable to connect: \n{type(exc).__name__}.")
        raise exc

    conn.autocommit = True
    cur = conn.cursor()

    sql_query = f"CREATE DATABASE IF NOT EXISTS {db_name}"

    try:
        cur.execute(sql_query)
    except Exception as exc:
        print("Cannot connect")
        print(f"{type(exc).__name__}")
        print(f"Query:{cur.query}")
        conn.close()
        cur.close()
        db_created = False
        return db_created
    else:
        conn.autocommit = False
        cur.close()
        conn.close()
        db_created = True
        return db_created


def connect_to_database(db_name, conn_info):
    try:
        conn = psycopg2.connect(
            database=db_name,
            host=conn_info['host'],
            user=conn_info['user'],
            password=conn_info['password'],
            port=conn_info['port'],
        )
        return conn
    except Exception as exc:
        print(f"Unable to connect: \n{type(exc).__name__}.")
        raise exc


def create_table(create_query, connection, cursor):
    try:
        cursor.execute(create_query)
    except Exception as exc:
        print(f"\n {type(exc).__name__}")
        print(f"Query:{cursor.query}")
        table_created = False
        return table_created
    else:
        cursor.close()
        connection.close()
        table_created = True
        return table_created


def run():
    conn_info = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PW,
    }
    database_created = create_db(DB_NAME, conn_info)

    creating_query = "CREATE TABLE IF NOT EXISTS daily_consumption (" \
                     "day_id SERIAL PRIMARY KEY, --AUTO_INCREMENT integer, as primary key" \
                     "creation_date  DATE," \
                     "date DATE,"\
                     "consumption FLOAT(8)"\
                     "cost FLOAT(8))"
    conn = connect_to_database(DB_NAME, conn_info)
    cur = conn.cursor()
    created_table = create_table(creating_query, conn, cur)


if __name__ == "__main__":
    run()
