#!/usr/bin/env python3

import pytest
from unittest.mock import MagicMock, Mock, patch, ANY
import responses
import os
from dotenv import load_dotenv
from holaluz_api import HolaLuz
from create_database import connect_to_database, execute_query
import datetime as dt
import json

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')
TABLE_NAME = os.getenv('TABLE_NAME')

DB_CONN_INFO = {
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


class TestClassIntegrationUpdateDatabase:
    @responses.activate
    def test_insert_in_db_from_json(self, path_to_json):
        with open(f'{path_to_json}', 'r') as f_obj:
            data_to_insert = f_obj.read()

        hl_api_consumption_json_reply = [
            {
                "cups": "cups",
                "daily": [
                    data_to_insert
                ]
            }
        ]

        responses.post(
            LOGIN_URL,
            json=HL_API_LOGIN_JSON_REPLY
        )
        
        