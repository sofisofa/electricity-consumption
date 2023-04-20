#!/usr/bin/env python3

import unittest
import responses
import datetime as dt
from src.electricity_consumption.holaluz_api import HolaLuz
from src.electricity_consumption.holaluz_api import run
from mockito import when, mock, verify, unstub
import json
import builtins
import os
from dotenv import load_dotenv

load_dotenv()


# Fixtures
def create_date(date, delta):
    new_date = dt.date.isoformat(date + dt.timedelta(days=delta))
    return new_date


USERNAME = os.getenv('HL_USER')
PW = os.getenv('HL_PASS')
LOGIN_PAYLOAD = {'_app': 'customer', '_username': USERNAME, '_password': PW}

LOGIN_URL = "https://core.holaluz.com/api/private/login_check"
CONSUMPTION_URL = "https://zc-consumption.holaluz.com/consumption"

API_LOGIN_JSON_REPLY = {
    "token": "token",
    "refresh_token": "refresh_token"
}

CONSUMPTION_DATA = [
    {'date': create_date(dt.date.today(), -1), 'total_consumption': 3.5, 'total_cost': 2},
    {'date': create_date(dt.date.today(), 0), 'total_consumption': -2, 'total_cost': -1},
    {'date': create_date(dt.date.today(), 1), 'total_consumption': 0.0, 'total_cost': 0.0},
    {'date': create_date(dt.date.today(), 2), 'total_consumption': 0, 'total_cost': 0},
]

CONSUMPTION_DATA_WITHOUT_ZERO_VALUES = [
    {'date': create_date(dt.date.today(), -1), 'total_consumption': 3.5, 'total_cost': 2},
    {'date': create_date(dt.date.today(), 0), 'total_consumption': -2, 'total_cost': -1},
]

API_CONSUMPTION_JSON_REPLY = [
    {
        "cups": "cups",
        "daily": [
            {
                "date": "2022-11-01",
                "total_consumption": 7.901000000000001,
                "total_cost": 3.48054689064485
            },
        ]
    }
]


class HolaluzTestCase(unittest.TestCase):
    
    def tearDown(self):
        unstub()
    
    @responses.activate
    def test_holaluz_login(self):
        # Given
        responses.post(
            LOGIN_URL,
            json=API_LOGIN_JSON_REPLY
        )
        
        # When
        hl = HolaLuz()
        # Then
        self.assertEqual(hl.api.token, "token")
    
    @responses.activate
    def test_holaluz_failed_login(self):
        expected_error_code = 404
        responses.post(
            LOGIN_URL,
            status=expected_error_code
        )
        
        with self.assertRaises(Exception) as cm:
            HolaLuz()
        
        the_exception = cm.exception
        self.assertTrue(f"{expected_error_code}" in str(the_exception))
    
    def test_clean_data(self):
        data = HolaLuz.clean_data(CONSUMPTION_DATA)
        self.assertEqual(CONSUMPTION_DATA_WITHOUT_ZERO_VALUES, data)
    
    @responses.activate
    def test_run_opens_file_and_calls_json_dump(self):
        api_consumption_json_reply = [{
            "cups": "cups",
            "daily": CONSUMPTION_DATA
        }]
        
        json_to_dump = {'creation date': dt.date.isoformat(dt.date.today()),
                        'daily_consumption': CONSUMPTION_DATA_WITHOUT_ZERO_VALUES}
        
        date = dt.date.fromisoformat(CONSUMPTION_DATA[0]["date"])
        month = date.strftime("%b")
        year = date.strftime("%y")
        
        responses.post(
            LOGIN_URL,
            json=API_LOGIN_JSON_REPLY
        )
        
        responses.get(
            CONSUMPTION_URL,
            json=api_consumption_json_reply
        )
        
        dummy_obj = mock()
        when(dummy_obj).__enter__(...).thenReturn(dummy_obj)
        when(dummy_obj).__exit__(...).thenReturn(None)
        when(builtins).open(
            f'./tests/consumption_files/hl_consumption_{month}_{year}.json', 'w').thenReturn(dummy_obj)
        when(json).dump(...).thenReturn()
        run()
        verify(json, times=1).dump(json_to_dump, dummy_obj)
        
    
if __name__ == "__main__":
    unittest.main()
