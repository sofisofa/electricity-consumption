#!/usr/bin/env python3

import pytest
import datetime as dt
from unittest.mock import MagicMock, Mock, patch
from .test_for_holaluz import create_date
import responses
from src.electricity_consumption import endesa_api


EN_USER = 'EN_USER'
EN_PW = 'EN_PASS'
LOGIN_URL = 'https://core.holaluz.com/api/private/login_check'
CONSUMPTION_URL = 'https://zc-consumption.holaluz.com/consumption'


class TestClassUpdateDatabase:
    def test_first(self):
        print('test')


if __name__ == "__main__":
    pytest.main([__file__])
