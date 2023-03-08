#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from electricity_consumption.holaluz_api import HolaLuz
from electricity_consumption.init_database import connect_to_database, execute_query
import datetime as dt
import json

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')
TABLE_NAME = os.getenv('TABLE_NAME')


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
                    insert_query = f"INSERT INTO {table_name} (creation_date, update_date, date, consumption, cost) " \
                                   f"VALUES (CURRENT_DATE, CURRENT_DATE, '{day['date']}', " \
                                   f"{day['total_consumption']}, {day['total_cost']} );"
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


def run():
    db_conn_info = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PW,
    }
    
    hl = HolaLuz()
    consumption_data = hl.retrieve_data()
    cleaned_data = hl.clean_data(consumption_data)
    
    conn = connect_to_database(DB_NAME, db_conn_info)
    insert_in_daily_consumption_db(cleaned_data, TABLE_NAME, conn)


if __name__ == "__main__":
    run()
