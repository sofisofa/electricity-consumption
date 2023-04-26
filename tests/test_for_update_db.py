#!/usr/bin/env python3
import pytest
import datetime as dt
from unittest.mock import MagicMock, Mock, patch
from .test_for_holaluz import create_date
import responses
from src.electricity_consumption import update_database
from src.electricity_consumption.endesa_api import Endesa

DB_NAME = 'DB_NAME'
DB_USER = 'DB_USER'
DB_PW = 'DB_PW'
DB_PORT = 'DB_PORT'
DB_HOST = 'DB_HOST'

HL_USER = 'HL_USER'
HL_PW = 'HL_PASS'
LOGIN_URL = 'https://core.holaluz.com/api/private/login_check'
CONSUMPTION_URL = 'https://zc-consumption.holaluz.com/consumption'

HL_API_LOGIN_JSON_REPLY = {
    "token": "token",
    "refresh_token": "refresh_token"
}
EN_USER = 'EN_USER'
EN_PW = 'EN_PASS'
EN_L_CUPS = {'Id': 'Id'}
EN_CYCLES = ['last cycle']
YESTERDAY = dt.date.today() - dt.timedelta(1)
TODAY = dt.date.today()
EN_MEASURED_CONSUMPTION = [
    [{'date': YESTERDAY.strftime('%d/%m/%Y'),
      'hourCCH': 1,
      'hour': '00 - 01 h',
      'invoiced': True,
      'typePM': '5',
      'valueDouble': 1,
      'obtainingMethod': 'R',
      'real': True,
      'value': '0,922'
      }],
    [{'date': TODAY.strftime('%d/%m/%Y'),
      'hourCCH': 5,
      'hour': '04 - 05 h',
      'invoiced': True,
      'typePM': '5',
      'valueDouble': 3.5,
      'obtainingMethod': 'R',
      'real': True,
      'value': '0,539'}]
]


HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES = [
    {'date': create_date(dt.date.today(), -1), 'total_consumption': 3.5, 'total_cost': 2},
    {'date': create_date(dt.date.today(), 0), 'total_consumption': -2, 'total_cost': -1},
]

EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES = [
    [
        {'date': create_date(dt.date.today(), -1), 'hour': '02:00:00', 'consumption': 1},
        {'date': create_date(dt.date.today(), 0), 'hour': '04:00:00', 'consumption': 3.5}
    ]
]

DB_TABLE_NAME = 'table'

HL_SELECT_LAST_DATE_QUERY = f"SELECT date FROM {DB_TABLE_NAME} " \
                             "ORDER BY date DESC " \
                             "LIMIT 1;"
EN_SELECT_LAST_DATE_QUERY = f"SELECT date FROM {DB_TABLE_NAME} " \
                             "ORDER BY hour DESC, date DESC " \
                             "LIMIT 1;"
HL_INSERT_QUERY = f"INSERT INTO {DB_TABLE_NAME} (creation_date, update_date, date, consumption, cost) " \
               f"VALUES (CURRENT_DATE, CURRENT_DATE, {HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['date']}, " \
               f"{HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['total_consumption']}, {HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['total_cost']} );"

EN_INSERT_QUERY = f"INSERT INTO {DB_TABLE_NAME} (creation_date, update_date, date, hour, consumption) " \
               f"VALUES (CURRENT_DATE, CURRENT_DATE, {EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[0][1]['date']}, " \
               f"{EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[0][1]['hour']}, {EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[0][1]['consumption']} );"


class TestClassUpdateDatabase:
    @pytest.fixture()
    def stub_connection(self):
        dummy_conn = Mock()
        dummy_conn.close.return_value = None
        dummy_conn.commit.return_value = None
        yield dummy_conn
        
    @pytest.fixture()
    def stub_cursor(self, stub_connection):
        dummy_conn = stub_connection
        dummy_cur = MagicMock()
        dummy_conn.cursor.return_value = dummy_cur
        dummy_cur.__enter__.return_value = dummy_cur
        dummy_cur.__exit__.return_value = None
        dummy_cur.close.return_value = None
        yield dummy_cur

    @pytest.fixture()
    def stub_env_var(self, monkeypatch):
        monkeypatch.setenv('HOLALUZ_ENABLED', 'True')
        monkeypatch.setenv('ENDESA_ENABLED', 'True')
        yield

    def test_insert_in_daily_consumption_db(self, stub_cursor, stub_connection):
        dummy_conn = stub_connection
        dummy_cur = stub_cursor
        dummy_cur.fetchone.return_value = [dt.date.today() - dt.timedelta(days=1)]
        dummy_cur.execute.side_effect = [None, None]

        inserted_data = update_database.insert_in_daily_consumption_db(HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES, DB_TABLE_NAME, dummy_conn)

        assert inserted_data == True

    def test_insert_in_daily_consumption_db_cannot_get_last_date(self, stub_cursor, stub_connection):
        dummy_conn = stub_connection
        dummy_cur = stub_cursor
        dummy_cur.fetchone.return_value = [None]
        dummy_cur.execute.side_effect = [Exception('oh no!'), None]

        with pytest.raises(Exception):
            update_database.insert_in_daily_consumption_db(HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES, DB_TABLE_NAME,
                                                           dummy_conn)

    def test_insert_in_daily_consumption_db_raises_exception(self, stub_cursor, stub_connection):
        dummy_conn = stub_connection
        dummy_cur = stub_cursor
        dummy_cur.fetchone.return_value = [dt.date.today() - dt.timedelta(days=1)]
        dummy_cur.execute.side_effect = [None, Exception('oh no!')]

        with pytest.raises(Exception):
            update_database.insert_in_daily_consumption_db(HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES, DB_TABLE_NAME, dummy_conn)

    def test_insert_in_hourly_consumption_db(self, stub_cursor, stub_connection):
        dummy_conn = stub_connection
        dummy_cur = stub_cursor
        dummy_cur.fetchone.return_value = [dt.date.today() - dt.timedelta(days=1), dt.time(hour=0)]
        dummy_cur.execute.side_effect = [None, None, None, None, None, None]

        inserted_data = update_database.insert_in_hourly_consumption_db(EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES, DB_TABLE_NAME, dummy_conn)

        assert inserted_data == True

    def test_insert_in_hourly_consumption_db_cannot_get_last_date(self, stub_cursor, stub_connection):
        dummy_conn = stub_connection
        dummy_cur = stub_cursor
        dummy_cur.fetchone.return_value = [None]
        dummy_cur.execute.side_effect = [Exception('oh no!'), None]

        with pytest.raises(Exception):
            update_database.insert_in_daily_consumption_db(EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES, DB_TABLE_NAME,
                                                           dummy_conn)

    def test_insert_in_hourly_consumption_db_raises_exception(self, stub_cursor, stub_connection):
        dummy_conn = stub_connection
        dummy_cur = stub_cursor
        dummy_cur.fetchone.return_value = [dt.date.today() - dt.timedelta(days=1), dt.time(hour=0)]
        dummy_cur.execute.side_effect = [None, Exception('oh no!')]

        with pytest.raises(Exception):
            update_database.insert_in_daily_consumption_db(EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES, DB_TABLE_NAME, dummy_conn)

# TODO: see if the following test can be inserted into the integration test
    
    # @responses.activate
    # @patch("src.electricity_consumption.endesa_api.Edistribucion")
    # @patch("psycopg2.connect")
    # def test_run_connects_to_db_and_inserts_data(self, mock_connect, mock_edis, stub_env_var):
    #     Endesa.edis = mock_edis.return_value
        # Endesa.edis.get_list_cups.return_value = [EN_L_CUPS]
        # Endesa.edis.get_list_cycles.return_value = EN_CYCLES
        # Endesa.edis.get_meas.return_value = EN_MEASURED_CONSUMPTION

        # hl_api_consumption_json_reply = [{
        #     "cups": "cups",
        #     "daily": HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES
        # }]

        # responses.post(
        #     LOGIN_URL,
        #     json=HL_API_LOGIN_JSON_REPLY
        # )
    
        # responses.get(
            # CONSUMPTION_URL,
            # json=hl_api_consumption_json_reply
        # )

        # expected_en_insert_query = f"INSERT INTO en_hourly_consumption (creation_date, update_date, date, hour, consumption) " \
                            # f"VALUES (CURRENT_DATE, CURRENT_DATE, {EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[0][1]['date']}, " \
                            # f"{EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[0][1]['hour']}, {EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[0][1]['consumption']} );"
        #
        # expected_hl_insert_query = "INSERT INTO daily_consumption (creation_date, update_date, date, consumption, cost) " \
        #                     f"VALUES (CURRENT_DATE, CURRENT_DATE, '{HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['date']}', " \
        #                     f"{HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['total_consumption']}, {HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['total_cost']} );"
        
        # dummy_conn = mock_connect.return_value
        # dummy_conn.close.return_value = None
        # dummy_conn.commit.return_value = None
        
        # dummy_cur = MagicMock()
        # dummy_conn.cursor.return_value = dummy_cur
        # dummy_cur.__enter__.return_value = dummy_cur
        # dummy_cur.__exit__.return_value = None
        # dummy_cur.fetchone.side_effect = [(dt.date.today() - dt.timedelta(days=1), dt.time(hour=3)), (dt.date.today() - dt.timedelta(days=1),)]
        # dummy_cur.execute.side_effect = [None, None, None, None, None, None, None, None]
        # dummy_cur.close.return_value = None
        # update_database.run()
        # dummy_cur.execute.assert_has_calls([expected_en_insert_query, expected_hl_insert_query], any_order=True)
    

if __name__ == "__main__":
    pytest.main([__file__])
    