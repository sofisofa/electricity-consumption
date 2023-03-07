#!/usr/bin/env python3
import pytest
import datetime as dt
from unittest.mock import MagicMock, Mock, patch, ANY
from .test_for_holaluz import create_date
from .. import update_database
import responses

DB_NAME = 'DB_NAME'
DB_USER = 'DB_USER'
DB_PW = 'DB_PW'
DB_PORT = 'DB_PORT'
DB_HOST = 'DB_HOST'

HL_USER= 'HL_USER'
HL_PW = 'HL_PASS'
LOGIN_URL = 'https://core.holaluz.com/api/private/login_check'
CONSUMPTION_URL = 'https://zc-consumption.holaluz.com/consumption'

API_LOGIN_JSON_REPLY = {
    "token": "token",
    "refresh_token": "refresh_token"
}

CONSUMPTION_DATA_WITHOUT_ZERO_VALUES = [
    {'date': create_date(dt.date.today(), -1), 'total_consumption': 3.5, 'total_cost' : 2 },
    {'date': create_date(dt.date.today(), 0), 'total_consumption': -2, 'total_cost' : -1},
]

DB_TABLE_NAME = 'table'

SELECT_LAST_DATE_QUERY = f"SELECT date FROM {DB_TABLE_NAME} " \
                             "ORDER BY date DESC " \
                             "LIMIT 1;"

INSERT_QUERY = f"INSERT INTO {DB_TABLE_NAME} (creation_date, update_date, date, consumption, cost) " \
               f"VALUES (CURRENT_DATE, CURRENT_DATE, {CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['date']}, " \
               f"{CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['total_consumption']}, {CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['total_cost']} );"


class TestClassUpdateDatabase:
    def test_insert_in_daily_consumption_db(self):
        #Given
        dummy_conn = Mock()
        dummy_conn.close.return_value = None
        dummy_conn.commit.return_value = None
        dummy_cur = MagicMock()
        dummy_conn.cursor.return_value = dummy_cur
        dummy_cur.__enter__.return_value = dummy_cur
        dummy_cur.__exit__.return_value = None
        dummy_cur.execute.side_effect = [create_date(dt.date.today(), -1), None]
        dummy_cur.close.return_value = None
        
        #When
        inserted_data = update_database.insert_in_daily_consumption_db(CONSUMPTION_DATA_WITHOUT_ZERO_VALUES, DB_TABLE_NAME, dummy_conn)
        
        #Then
        assert inserted_data == True

    def test_insert_in_daily_consumption_db_raises_exception(self):
        # Given
        
        dummy_conn = Mock()
        dummy_conn.commit.return_value = None
        dummy_conn.close.return_value = None
        dummy_cur = MagicMock()
        dummy_conn.cursor.return_value = dummy_cur
        dummy_cur.__enter__.return_value = dummy_cur
        dummy_cur.__exit__.return_value = None
        dummy_cur.execute.side_effect = [create_date(dt.date.today(), -1), Exception('oh no!')]
        dummy_cur.close.return_value = None
        
        #When
        
        # Then
        with pytest.raises(Exception):
            inserted_data = update_database.insert_in_daily_consumption_db(CONSUMPTION_DATA_WITHOUT_ZERO_VALUES, DB_TABLE_NAME,
                                                           dummy_conn)
    
    @responses.activate
    @patch("psycopg2.connect")
    def test_run_connects_to_db_and_inserts_data(self, mock_connect):
        hl_api_consumption_json_reply = [{
            "cups": "cups",
            "daily": CONSUMPTION_DATA_WITHOUT_ZERO_VALUES
        }]

        responses.post(
            LOGIN_URL,
            json=API_LOGIN_JSON_REPLY
        )
    
        responses.get(
            CONSUMPTION_URL,
            json=hl_api_consumption_json_reply
        )
        
        expected_insert_query = "INSERT INTO daily_consumption (creation_date, update_date, date, consumption, cost) " \
                                f"VALUES (CURRENT_DATE, CURRENT_DATE, {CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['date']}, " \
                                f"{CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['total_consumption']}, {CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['total_cost']} );"
        
        dummy_conn = mock_connect.return_value
        dummy_conn.close.return_value = None
        dummy_conn.commit.return_value = None
        
        dummy_cur = MagicMock()
        dummy_conn.cursor.return_value = dummy_cur
        dummy_cur.__enter__.return_value = dummy_cur
        dummy_cur.__exit__.return_value = None
        dummy_cur.execute.side_effect = [create_date(dt.date.today(), -1), None]
        dummy_cur.close.return_value = None
        update_database.run()
        dummy_cur.execute.assert_called_with(expected_insert_query)

        
if __name__ == "__main__":
    pytest.main([__file__])
    