#!/usr/bin/env python3

import logging
import psycopg2
from distutils.util import strtobool
import os
from dotenv import load_dotenv

# TODO:
#   -refactor with SQLAlchemy

if os.getenv('ENV_FILE_PATH'):
    envFilePath = os.getcwd() + os.getenv('ENV_FILE_PATH')
    load_dotenv(envFilePath, override=True)
else:
    load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')

HL_TABLE_NAME = os.getenv('HL_TABLE_NAME')

EN_TABLE_NAME = os.getenv('EN_TABLE_NAME')


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
        logging.error(f"Unable to connect to database: \n{type(exc).__name__}.")
        raise exc


def execute_query(query, connection):
    """Executes a SQL query, given the connection to a Postgres database."""
    with connection.cursor() as cursor:
        cursor.execute(query)


def run():
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S',
                        filename='/tmp/electricityconsumption.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)

    """Connects to database and creates the table in case it was not already created"""
    conn_info = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PW,
    }

    if strtobool(os.getenv('ENDESA_ENABLED')):
        creating_table_query = f"CREATE TABLE IF NOT EXISTS {EN_TABLE_NAME} (" \
                               "id BIGSERIAL PRIMARY KEY, " \
                               "datetime TIMESTAMPTZ, " \
                               "consumption FLOAT(8), " \
                               "creation_date  TIMESTAMPTZ, " \
                               "modified_date  TIMESTAMPTZ);" \

        
        with connect_to_database(DB_NAME, conn_info) as conn:
            logging.info(f"Creating table: {EN_TABLE_NAME}.")
            try:
                execute_query(creating_table_query, conn)
            except Exception as exc:
                logging.error(f"Unable to create table: \n {type(exc).__name__}")
                raise exc
            
            conn.commit()

    if strtobool(os.getenv('HOLALUZ_ENABLED')):
        creating_table_query = f"CREATE TABLE IF NOT EXISTS {HL_TABLE_NAME} (" \
                               "id BIGSERIAL PRIMARY KEY, " \
                               "date DATE, " \
                               "consumption FLOAT(8), " \
                               "cost FLOAT(8), " \
                               "creation_date TIMESTAMPTZ, " \
                               "modified_date  TIMESTAMPTZ);"

        with connect_to_database(DB_NAME, conn_info) as conn:
            logging.info(f"Creating table: {HL_TABLE_NAME}.")
            try:
                execute_query(creating_table_query, conn)
            except Exception as exc:
                logging.error(f"Unable to create table: \n {type(exc).__name__}")
                raise exc
            
            conn.commit()


if __name__ == "__main__":
    run()
