#!/usr/bin/env python3

import pytest
import os
from dotenv import load_dotenv
import responses
import json
from .. import update_database
from ..init_database import execute_query, connect_to_database

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')
TABLE_NAME = os.getenv('TABLE_NAME')

CONN_INFO = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PW,
    }

LOGIN_URL = 'https://core.holaluz.com/api/private/login_check'
CONSUMPTION_URL = 'https://zc-consumption.holaluz.com/consumption'

HL_API_LOGIN_JSON_REPLY = {
    "token": "token",
    "refresh_token": "refresh_token"
}

PATH_TO_JSON = os.getenv('PATH_TO_JSON')


class TestClassIntegrationUpdateDatabase:
    @responses.activate
    def test_api_reply_stored_in_db(self):
        
        with open(f'{PATH_TO_JSON}', 'r') as f_obj:
            json_to_dict= json.load(f_obj)
            
        data_to_insert = json_to_dict["daily_consumption"]

        hl_api_consumption_json_reply = [
            {
                "cups": "cups",
                "daily": data_to_insert
                
            }
        ]

        responses.post(
            LOGIN_URL,
            json=HL_API_LOGIN_JSON_REPLY
        )
        
        responses.get(
            CONSUMPTION_URL,
            json=hl_api_consumption_json_reply
        )
        
        update_database.run()
        
        expected_number_of_rows = len(data_to_insert)
        
        count_query = f'SELECT COUNT(day_id) FROM {TABLE_NAME}'
        with connect_to_database(DB_NAME, CONN_INFO) as conn:
            with conn.cursor() as cur:
                cur.execute(count_query)
                rows_inserted = cur.fetchall()
            
        assert rows_inserted == expected_number_of_rows


if __name__ == "__main__":
    pytest.main([__file__])
