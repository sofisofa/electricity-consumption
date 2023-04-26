#!/usr/bin/env python3

import pytest
import datetime as dt
from unittest.mock import MagicMock, Mock, patch
from .test_for_holaluz import create_date
import responses
from src.electricity_consumption import endesa_api as ea
from src.electricity_consumption.endesa_api import Endesa, Edistribucion

EN_USER = 'EN_USER'
EN_PW = 'EN_PASS'
LOGIN_URL = 'https://core.holaluz.com/api/private/login_check'
CONSUMPTION_URL = 'https://zc-consumption.holaluz.com/consumption'

L_CUPS = {'Id': 'Id'}
CYCLES = ['last cycle']
MEASURED_CONSUMPTION = [[
    {'date': '08/03/2023',
     'hourCCH': 1,
     'hour': '00 - 01 h',
     'invoiced': True,
     'typePM': '5',
     'valueDouble': 0.922,
     'obtainingMethod': 'R',
     'real': True,
     'value': '0,922'
     },
    {'date': '08/03/2023',
     'hourCCH': 2,
     'hour': '01 - 02 h',
     'invoiced': True,
     'typePM': '5',
     'valueDouble': 0.539,
     'obtainingMethod': 'R',
     'real': True,
     'value': '0,539'
     }
]]
EXPECTED_CONSUMPTION_DATA = [[
    {'date': '08/03/2023',
     'hour': 1,
     'label': '00 - 01 h',
     'consumption': 0.922
     },
    {'date': '08/03/2023',
     'hour': 2,
     'label': '01 - 02 h',
     'consumption': 0.539,
     }
    
]]

EXPECTED_REFORMAT_DATA = [[
    {'date': '2023-03-08', 'hour': '00:00:00', 'label': '00 - 01 h', 'consumption': 0.922},
    {'date': '2023-03-08', 'hour': '01:00:00', 'label': '01 - 02 h', 'consumption': 0.539}
]]


class TestClassUpdateDatabase:
    @patch("src.electricity_consumption.endesa_api.Edistribucion")
    def test_get_last_consumption_data(self, mock):
        Endesa.edis = mock.return_value
        Endesa.edis.get_list_cups.return_value = [L_CUPS]
        Endesa.edis.get_list_cycles.return_value = CYCLES
        Endesa.edis.get_meas.return_value = MEASURED_CONSUMPTION
        
        #When
        en = ea.Endesa(EN_USER, EN_PW)
        
        #Then
        data = en.get_last_consumption_data()
        Endesa.edis.get_list_cycles.assert_called_with('Id')
        Endesa.edis.get_meas.assert_called_with(L_CUPS['Id'], CYCLES[0])
        assert data == EXPECTED_CONSUMPTION_DATA
        
    def test_reformat_data(self):
        data = Endesa.reformat_data(EXPECTED_CONSUMPTION_DATA)
        assert data == EXPECTED_REFORMAT_DATA

    @patch("src.electricity_consumption.endesa_api.Edistribucion")
    @patch("src.electricity_consumption.endesa_api.json.dump")
    @patch("builtins.open")
    def test_run_opens_file_and_calls_json_dump(self, mock_open, mock_dump, mock_edis):
        Endesa.edis = mock_edis.return_value
        Endesa.edis.get_list_cups.return_value = [L_CUPS]
        Endesa.edis.get_list_cycles.return_value = CYCLES
        Endesa.edis.get_meas.return_value = MEASURED_CONSUMPTION

        date = dt.date.fromisoformat(EXPECTED_REFORMAT_DATA[0][0]["date"])
        month = date.strftime("%b")
        year = date.strftime("%y")

        dummy_obj = MagicMock()
        dummy_obj.__enter__.return_value = dummy_obj
        dummy_obj.__exit__.return_value = None
        mock_open.return_value = dummy_obj
        consumption_json = {'creation date': dt.date.isoformat(dt.date.today()),
                            'hourly_consumption': EXPECTED_REFORMAT_DATA}

        ea.run()
        mock_open.assert_called_with(f'./tests/consumption_files/en_consumption_{month}_{year}.json', 'w')
        mock_dump.assert_called_with(consumption_json, dummy_obj)


if __name__ == "__main__":
    pytest.main([__file__])
