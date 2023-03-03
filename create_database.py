#!/usr/bin/env python3

import psycopg2
import os
from dotenv import load_dotenv

# TODO:
#   -refactor with SQLAlchemy
#   -autocommit ("with cur as conn.cursor()...")

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')
TABLE_NAME = os.getenv('TABLE_NAME')


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
    
    search_db_query = f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'"
    cur.execute(search_db_query)
    exists = cur.fetchone()
    if not exists:
        create_db_query = f"CREATE DATABASE {db_name}"
        
        try:
            cur.execute(create_db_query)
            db_created = True
        except Exception as exc:
            print("Cannot create database")
            print(f"{type(exc).__name__}")
            print(f"Query:{cur.query}")
            db_created = False
        finally:
            conn.autocommit = False
            cur.close()
            conn.close()
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
    with connection.cursor() as cursor:
        cursor.execute(query)


def run():
    conn_info = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PW,
    }
    
    database_created_or_existing = create_db(DB_NAME, conn_info)
    
    creating_table_query = f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (" \
                           "day_id BIGSERIAL PRIMARY KEY, " \
                           "creation_date  DATE, " \
                           "update_date  DATE, " \
                           "date DATE, " \
                           "consumption FLOAT(8), " \
                           "cost FLOAT(8));"
    
    with connect_to_database(DB_NAME, conn_info) as conn:
        try:
            execute_query(creating_table_query, conn)
        except Exception as exc:
            print(f"Unable to create table: \n {type(exc).__name__}")
            raise exc
        
        conn.commit()


if __name__ == "__main__":
    run()
