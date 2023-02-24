#!/usr/bin/env python3

import psycopg2
import os
from dotenv import load_dotenv

#TODO:
#   -refactor with SQLAlchemy
#   -autocommit ("with cur as conn.cursor()...")

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
    
    search_query = f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'"
    cur.execute(search_query)
    exists = cur.fetchone()
    if not exists:
        create_db_query = f"CREATE DATABASE {db_name}"
    
        try:
            cur.execute(create_db_query)
        except Exception as exc:
            print("Cannot create database")
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
    else:
        return exists


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


def execute_query(query, connection):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
    except Exception as exc:
        print(f"\n {type(exc).__name__}")
        print(f"Query:{cursor.query}")
        cursor.close()
        query_executed = False
        return query_executed
    else:
        cursor.close()
        query_executed = True
        return query_executed


def run():
    conn_info = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PW,
    }
    
    database_created_or_existing = create_db(DB_NAME, conn_info)

    creating_table_query = "CREATE TABLE IF NOT EXISTS daily_consumption (" \
                     "day_id BIGSERIAL PRIMARY KEY, " \
                     "creation_date  DATE, " \
                     "update_date  DATE, " \
                     "date DATE, "\
                     "consumption FLOAT(8), "\
                     "cost FLOAT(8));"

    conn = connect_to_database(DB_NAME, conn_info)
    created_table = execute_query(creating_table_query, conn)

    conn.commit()

    conn.close()


if __name__ == "__main__":
    run()
