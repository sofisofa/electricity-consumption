import unittest
import responses
import datetime as dt
from holaluz_api import HolaLuz
from holaluz_api import run
from mockito import when, mock, verify, unstub
import json
import builtins

def create_date(date, delta):
            new_date = dt.date.isoformat(date + dt.timedelta(days = delta))
            return new_date


class HolaluzTestCase(unittest.TestCase):
        
    def setUp(self):
        self.login_url = "https://core.holaluz.com/api/private/login_check"
        self.consumption_url =  "https://zc-consumption.holaluz.com/consumption"
        self.api_login_json_reply = {
                "token": "token",
                "refresh_token" : "refresh_token"
                }
        
        self.consumption_data =  [
            {'date': create_date(dt.date.today(), -1), 'total_consumption': 3.5},
            {'date': create_date (dt.date.today(), 0), 'total_consumption': -2},
            {'date': create_date(dt.date.today(), 1), 'total_consumption': 0.0},
            {'date': create_date(dt.date.today(), 2), 'total_consumption': 0},
        ]
        
        self.api_consumption_json_reply = {
                "cups" : "cups",
                "daily" : "daily"
                }
       
        
        self.consumption_data_without_zero_values = [
            {'date': create_date(dt.date.today(), -1), 'total_consumption': 3.5},
            {'date': create_date (dt.date.today(), 0), 'total_consumption': -2},
        ]
        
    def tearDown(self):
         unstub()
    
    @responses.activate
    def test_holaluz_login(self):
        # Given
        responses.post(
            self.login_url,
              json = self.api_login_json_reply
              )

        # When
        hl = HolaLuz()
        # Then
        self.assertEqual(hl.token, "token")

    @responses.activate
    def test_holaluz_failed_login(self):
        expected_error_code = 404
        responses.post(
            self.login_url,
            status = expected_error_code
              )

        with self.assertRaises(Exception) as cm:
            HolaLuz()

        the_exception = cm.exception
        self.assertTrue(f"{expected_error_code}" in str(the_exception))

    @responses.activate
    def test_holaluz_retrieve_data(self):
        responses.post(
           self.login_url,
              json = self.api_login_json_reply
              )

        responses.get(
            self.consumption_url,
            json = self.api_consumption_json_reply
              )
            
        hl = HolaLuz()
        data = hl.retrieve_data()
        self.assertEqual("daily", data)


    @responses.activate
    def test_failed_retrieve_data(self):
        expected_error_code = 404
        responses.post(
            self.login_url,
              json = self.api_login_json_reply
              )

        responses.get(
            self.consumption_url,
            status = expected_error_code
              )
            
        with self.assertRaises(Exception) as cm:
            hl = HolaLuz()
            hl.retrieve_data()

        the_exception = cm.exception
        self.assertTrue(f"{expected_error_code}" in str(the_exception))

    def test_clean_data(self):
        
        data = HolaLuz.clean_data(self.consumption_data)
        self.assertEqual(self.consumption_data_without_zero_values, data)

    @responses.activate
    def test_run_calls_json_dump_when_successful(self):
        api_consumption_json_reply = {
            "cups" : "cups",
            "daily" : self.consumption_data
        }
       
        responses.post(
            self.login_url,
              json = self.api_login_json_reply
              )


        responses.get(
            self.consumption_url,
            json = api_consumption_json_reply
              )
        
        
        when(json).dump(...).thenReturn()
        run()
        verify(json, times = 1).dump(...)
        
    @responses.activate
    def test_run_opens_file_and_calls_json_dump(self):
        api_consumption_json_reply = {
            "cups" : "cups",
            "daily" : self.consumption_data
        }
        
        json_to_dump = {'creation date'  : dt.date.isoformat(dt.date.today()),
            'daily_consumption': self.consumption_data_without_zero_values}
        
        date = dt.date.fromisoformat(self.consumption_data[0]["date"])
        month = date.strftime("%b")
        year = date.strftime("%y")
       
        responses.post(
            self.login_url,
              json = self.api_login_json_reply
              )


        responses.get(
            self.consumption_url,
            json = api_consumption_json_reply
              )
        
        dummy_obj = mock()
        when(dummy_obj).__enter__(...).thenReturn(dummy_obj)
        when(dummy_obj).__exit__(...).thenReturn(None)
        when(builtins).open(f'.\consumption_files\consumption_{month}_{year}.json','a').thenReturn(dummy_obj)
        when(json).dump(...).thenReturn()
        run()
        verify(json, times = 1).dump(json_to_dump,dummy_obj)
        

if __name__ == "__main__":
    unittest.main()