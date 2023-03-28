#!/usr/bin/env python3

import logging
import psycopg2
import os
from dotenv import load_dotenv

# TODO:
#   -refactor with SQLAlchemy

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')
TABLE_NAME = os.getenv('TABLE_NAME')


def connect_to_database(db_name, conn_info):
    """Connects to a Postgres database.
    
    Parameters:
        -db_name: string, name of the database
        -conn_info: dict, containing information for the connection
                {
                "host": DB_HOST,
                "port": DB_PORT,
                "user": DB_USER,
                "password": DB_PW,
                }
        
    """
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
    """Executes a SQL query, given the connection to a Postgres database."""
    with connection.cursor() as cursor:
        cursor.execute(query)


def run():
    """Connects to database and creates the table in case it was not already created"""
    conn_info = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PW,
    }
    
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
