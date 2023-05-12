#!/usr/bin/env python3

import os

from dotenv import load_dotenv
from distutils.util import strtobool
import datetime as dt
from holaluz_api import HolaLuz
from endesa_api import Endesa
from init_database import connect_to_database, execute_query

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


def insert_in_daily_consumption_db(data_to_insert, table_name, db_conn):
    """This method inserts the data in a table,
    if their date is after than the last date inserted in the table.
    
    Parameters:
        -data: should be similar to holaluz_api cleaned data
        -db_name: name of the database
        -db_conn: connection to the database
    """
    
    with db_conn.cursor() as cur:
        select_last_date_query = f"SELECT date FROM {table_name} " \
                                 "ORDER BY date DESC " \
                                 "LIMIT 1;"
        try:
            cur.execute(select_last_date_query)
            fetched = cur.fetchone()
            if fetched is None:
                last_date = fetched
            else:
                last_date = fetched[0]
        except Exception as exc:
            print(f"Unable to get last date: \n{type(exc).__name__}.")
            raise exc
        
        for day in data_to_insert:
            if last_date is None or dt.date.fromisoformat(day['date']) > last_date:
                try:
                    insert_query = f"INSERT INTO {table_name} (date, consumption, cost, creation_date, modified_date) " \
                                   f"VALUES ('{day['date']}', " \
                                   f"{day['total_consumption']}, {day['total_cost']}, " \
                                   f"CURRENT_TIMESTAMP(2) at time zone 'UTC', CURRENT_TIMESTAMP(2) at time zone 'UTC');"
                    execute_query(insert_query, db_conn)
                except Exception as exc:
                    print(f"Unable to insert data: \n{type(exc).__name__}.")
                    db_conn.close()
                    inserted_data = False
                    raise exc
                else:
                    inserted_data = True
            else:
                inserted_data = False
    db_conn.commit()
    db_conn.close()
    
    return inserted_data


def get_last_inserted_datetime(table_name, db_conn):
    with db_conn.cursor() as cur:
        select_last_date_and_hour_query = f"SELECT datetime FROM {table_name} " \
                                          "ORDER BY datetime DESC " \
                                          "LIMIT 1;"
        try:
            cur.execute(select_last_date_and_hour_query)
            fetched = cur.fetchone()
            if fetched is None:
                last_datetime = fetched
            else:
                last_datetime = fetched[0]
        except Exception as exc:
            print(f"Unable to get last date: \n{type(exc).__name__}.")
            raise exc
    return last_datetime


def insert_in_hourly_consumption_db(data_to_insert, table_name, db_conn):
    """This method inserts the data in a table,
    if their date and hour is after than the last date and hour inserted in the table.

    Parameters:
        -data: should be similar to endesa_api consumption data (after reformat)
        -db_name: name of the database
        -db_conn: connection to the database
    """
    
    last_datetime = get_last_inserted_datetime(table_name, db_conn)
    inserted_data = False
    for day in data_to_insert:
        if last_datetime is None or dt.datetime.fromisoformat(day[-1]['datetime']) > last_datetime:
            for hour in day:
                try:
                    insert_query = f"INSERT INTO {table_name} (datetime, consumption, creation_date, modified_date) " \
                                   f"VALUES ('{hour['datetime']}', {hour['consumption']}, " \
                                   f"CURRENT_TIMESTAMP(2) at time zone 'UTC', CURRENT_TIMESTAMP(2) at time zone 'UTC');"
                    execute_query(insert_query, db_conn)
                except Exception as exc:
                    print(f"Unable to insert data: \n{type(exc).__name__}.")
                    db_conn.close()
                    raise exc
                else:
                    inserted_data = True
            
    if not inserted_data:
        print('Data already up to date!')
    
    db_conn.commit()
    db_conn.close()
    
    return inserted_data


def run():
    db_conn_info = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PW,
    }
    
    if strtobool(os.getenv('ENDESA_ENABLED')):
        en = Endesa(os.getenv('EN_USER'), os.getenv('EN_PASS'))
        conn = connect_to_database(DB_NAME, db_conn_info)
        
        last_inserted_datetime = get_last_inserted_datetime(EN_TABLE_NAME, conn)
        
        if last_inserted_datetime is not None:
            consumption_data = en.get_interval_consumption_data(dt.date.isoformat(last_inserted_datetime),
                                                                dt.date.isoformat(dt.date.today()))
        else:
            consumption_data = en.get_last_invoiced_consumption_data()
            
        consumption_data = en.reformat_data(consumption_data)
        
        insert_in_hourly_consumption_db(consumption_data, EN_TABLE_NAME, conn)
    
    if strtobool(os.getenv('HOLALUZ_ENABLED')):
        hl = HolaLuz()
        consumption_data = hl.api.retrieve_data()
        cleaned_data = hl.clean_data(consumption_data)
        
        conn = connect_to_database(DB_NAME, db_conn_info)
        insert_in_daily_consumption_db(cleaned_data, HL_TABLE_NAME, conn)


if __name__ == "__main__":
    run()
