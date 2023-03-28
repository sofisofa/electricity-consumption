#!/usr/bin/env python3

import pytest
from src.electricity_consumption.api_interactions import Api
import responses

LOGIN_URL = "https://example/login"
CONSUMPTION_URL = "https://example/consumption"

API_INFO = {
        'user': 'user',
        'pw': 'pw',
        'login_url': LOGIN_URL,
        'consumption_url': CONSUMPTION_URL,
        'login_payload': 'login_payload'
    }

API_LOGIN_JSON_REPLY = {
    "token": "token",
    "refresh_token": "refresh_token"
}


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


class TestClassApiInteractions:

    @responses.activate
    def test_api_login(self):
        # Given
        responses.post(
            LOGIN_URL,
            json=API_LOGIN_JSON_REPLY
        )
        
        # When
        api = Api(API_INFO)
        # Then
        assert api.token == "token"
    
    @responses.activate
    def test_api_failed_login(self):
        expected_error_code = 404
        responses.post(
            LOGIN_URL,
            status=expected_error_code
        )

        with pytest.raises(Exception):
            Api(API_INFO)
    
    @responses.activate
    def test_api_retrieve_data(self):
        responses.post(
            LOGIN_URL,
            json=API_LOGIN_JSON_REPLY
        )
        
        responses.get(
            CONSUMPTION_URL,
            json=API_CONSUMPTION_JSON_REPLY
        )
        
        api = Api(API_INFO)
        data = api.retrieve_data()
        
        assert [
            {
                "date": "2022-11-01",
                "total_consumption": 7.901000000000001,
                "total_cost": 3.48054689064485
            }
        ] == data
    
    @responses.activate
    def test_failed_retrieve_data(self):
        expected_error_code = 404
        responses.post(
            LOGIN_URL,
            json=API_LOGIN_JSON_REPLY
        )
        
        responses.get(
            CONSUMPTION_URL,
            status=expected_error_code
        )
        
        with pytest.raises(Exception) as cm:
            api = Api(API_INFO)
            api.retrieve_data()
        
        assert f"{expected_error_code}" in str(cm.value)
    
    @responses.activate
    def test_retrieved_empty_data(self):
        responses.post(
            LOGIN_URL,
            json=API_LOGIN_JSON_REPLY
        )
        
        responses.get(
            CONSUMPTION_URL,
            json=[{
                "cups": "cups",
                "daily": []
            }]
        )
        expected_error = 'Data retrieved but is empty!'
        with pytest.raises(Exception) as cm:
            api = Api(API_INFO)
            api.retrieve_data()

        assert f"{expected_error}" == str(cm.value)
    

if __name__ == "__main__":
    pytest.main([__file__])
