#!/usr/bin/env python3
import pytest
import datetime as dt
from unittest.mock import MagicMock, Mock
from .test_for_holaluz import create_date
from src.electricity_consumption import update_database

# database global variables
DB_NAME = 'DB_NAME'
DB_USER = 'DB_USER'
DB_PW = 'DB_PW'
DB_PORT = 'DB_PORT'
DB_HOST = 'DB_HOST'
DB_TABLE_NAME = 'table'


# Holaluz global variables
LOGIN_URL = 'https://core.holaluz.com/api/private/login_check'
CONSUMPTION_URL = 'https://zc-consumption.holaluz.com/consumption'

HL_API_LOGIN_JSON_REPLY = {
    "token": "token",
    "refresh_token": "refresh_token"
}

HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES = [
    {'date': create_date(dt.date.today(), -1), 'total_consumption': 3.5, 'total_cost': 2},
    {'date': create_date(dt.date.today(), 0), 'total_consumption': -2, 'total_cost': -1},
]

HL_SELECT_LAST_DATE_QUERY = f"SELECT date FROM {DB_TABLE_NAME} " \
                             "ORDER BY date DESC " \
                             "LIMIT 1;"

HL_INSERT_QUERY = f"INSERT INTO {DB_TABLE_NAME} (creation_date, update_date, date, consumption, cost) " \
               f"VALUES (CURRENT_DATE, CURRENT_DATE, {HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['date']}, " \
               f"{HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['total_consumption']}, {HL_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES[1]['total_cost']} );"


# Endesa global variable
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

EN_CONSUMPTION_DATA_WITHOUT_ZERO_VALUES = [
    [
        {'date': create_date(dt.date.today(), -1), 'hour': '02:00:00', 'consumption': 1},
        {'date': create_date(dt.date.today(), 0), 'hour': '04:00:00', 'consumption': 3.5}
    ]
]

EN_SELECT_LAST_DATE_QUERY = f"SELECT date FROM {DB_TABLE_NAME} " \
                             "ORDER BY hour DESC, date DESC " \
                             "LIMIT 1;"

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


if __name__ == "__main__":
    pytest.main([__file__])
    