#!/usr/bin/env python3

import pytest
import os
from dotenv import load_dotenv
import responses
import json
from unittest.mock import patch
from src.electricity_consumption import update_database
from src.electricity_consumption import init_database
from src.electricity_consumption.init_database import connect_to_database

load_dotenv()

# database global variables
DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')
CONN_INFO = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PW,
    }

# Holaluz global variables
HL_TABLE_NAME = os.getenv('HL_TABLE_NAME')

LOGIN_URL = 'https://core.holaluz.com/api/private/login_check'
CONSUMPTION_URL = 'https://zc-consumption.holaluz.com/consumption'

HL_API_LOGIN_JSON_REPLY = {
    "token": "token",
    "refresh_token": "refresh_token"
}

HL_PATH_TO_JSON = os.getenv('HL_PATH_TO_JSON')

# Endesa global variables
EN_TABLE_NAME = os.getenv('EN_TABLE_NAME')

EN_L_CUPS = {'Id': 'Id'}
EN_CYCLES = ['last cycle']

EN_PATH_TO_JSON = os.getenv('EN_PATH_TO_JSON')


def nest_length(nlist):
    if isinstance(nlist, list):
        return sum(nest_length(elem) for elem in nlist)
    else:
        return 1


class TestClassIntegrationUpdateDatabase:
    """Integration test: collects data stored in a .json in tests and updates the test db with it."""
    @pytest.fixture()
    def stub_env_var(self, monkeypatch):
        monkeypatch.setenv('HOLALUZ_ENABLED', 'True')
        monkeypatch.setenv('ENDESA_ENABLED', 'True')
        yield
    
    
    @responses.activate
    @patch("src.electricity_consumption.endesa_api.Edistribucion.__init__")
    @patch("src.electricity_consumption.update_database.Endesa.get_last_consumption_data")
    def test_api_reply_stored_in_db(self, mock_get_last_cons, mock_edis_init, stub_env_var):
        # Mock the call to Endesa
        mock_edis_init.return_value = None
        
        with open(f'{EN_PATH_TO_JSON}', 'r') as f_obj:
            json_to_dict = json.load(f_obj)
        
        en_data_to_insert = json_to_dict['hourly_consumption']
        mock_get_last_cons.return_value = en_data_to_insert
        
        # Mock the call to Holaluz
        with open(f'{HL_PATH_TO_JSON}', 'r') as f_obj:
            json_to_dict = json.load(f_obj)
            
        hl_data_to_insert = json_to_dict['daily_consumption']

        hl_api_consumption_json_reply = [
            {
                "cups": "cups",
                "daily": hl_data_to_insert
                
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

        # Run the update
        init_database.run()
        update_database.run()
        
        # Assertions for Endesa
        count_query = f'SELECT COUNT(id) FROM {EN_TABLE_NAME}'
        with connect_to_database(DB_NAME, CONN_INFO) as conn:
            with conn.cursor() as cur:
                cur.execute(count_query)
                rows_inserted = cur.fetchone()[0]

        expected_number_of_rows = nest_length(en_data_to_insert)
        assert rows_inserted == expected_number_of_rows
        
        # Assertions for Holaluz
        expected_number_of_rows = len(hl_data_to_insert)
        
        count_query = f'SELECT COUNT(id) FROM {HL_TABLE_NAME}'
        with connect_to_database(DB_NAME, CONN_INFO) as conn:
            with conn.cursor() as cur:
                cur.execute(count_query)
                rows_inserted = cur.fetchone()[0]
            
        assert rows_inserted == expected_number_of_rows


if __name__ == "__main__":
    pytest.main([__file__])
