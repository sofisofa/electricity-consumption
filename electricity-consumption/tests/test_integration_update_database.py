#!/usr/bin/env python3

import pytest

from unittest.mock import MagicMock, Mock, patch, ANY
from test_for_holaluz import create_date
import update_database
import responses

class TestClassIntegrationUpdateDatabase:
    @patch("psycopg2.connect")
    def test_insert_in_db_from_file(self, mock_connect):
        
        dummy_f_obj = MagicMock()
        builtins.open.return_value = dummy_f_obj
        dummy_f_obj.read.return_value = CONSUMPTION_DATA_WITHOUT_ZERO_VALUES
        
        data_to_insert = update_database.insert_in_db_from_file('this is a path')
        
        assert data_to_insert == CONSUMPTION_DATA_WITHOUT_ZERO_VALUES