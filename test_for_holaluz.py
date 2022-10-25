import unittest
import responses
import datetime as dt
from holaluz_api import HolaLuz

def create_date(date, delta):
            new_date = dt.date.isoformat(date + dt.timedelta(days = delta))
            return new_date


class HolaluzTestCase(unittest.TestCase):
        
    def setUp(self):
        self.login_url = "https://core.holaluz.com/api/private/login_check"
        self.consumption_url =  "https://zc-consumption.holaluz.com/consumption"
        self.login_json = {
                "token": "token",
                "refresh_token" : "refresh_token"
                }
        self.simple_data = {
                "cups" : "cups",
                "daily" : "daily"
                }
        self.data =  [
            {'date': create_date(dt.date.today(), -1), 'total_consumption': 3.5},
            {'date': create_date (dt.date.today(), 0), 'total_consumption': -2},
            {'date': create_date(dt.date.today(), 1), 'total_consumption': 0.0},
            {'date': create_date(dt.date.today(), 2), 'total_consumption': 0},
        ]
    
    @responses.activate
    def test_holaluz_login(self):
        # Given
        responses.post(
            self.login_url,
              json = self.login_json
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
              json = self.login_json
              )

        responses.get(
            self.consumption_url,
            json = self.simple_data
              )
            
        hl = HolaLuz()
        data = hl.retrieve_data()
        self.assertEqual("daily", data)


    @responses.activate
    def test_holaluz_failed_retrieve_data(self):
        expected_error_code = 404
        responses.post(
            self.login_url,
              json = self.login_json
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
        
        data = HolaLuz.clean_data(self.data)
        self.assertEqual(
            [{'date': create_date(dt.date.today(), -1), 'total_consumption': 3.5},
            {'date': create_date (dt.date.today(), 0), 'total_consumption': -2}], data)

    # @responses.activate
    # def test_holaluz_run(self):
    #     responses.post(
    #         "https://core.holaluz.com/api/private/login_check",
    #           json = {
    #             "token": "token",
    #              "refresh_token" : "refresh_token"
    #              }
    #           )

    #     responses.get(
    #         "https://zc-consumption.holaluz.com/consumption",
    #         json =  { "cups": "cups",
    #             "daily":  [
    #         {'date': create_date(dt.date.today(), -1), 'total_consumption': 3.5},
    #         {'date': create_date (dt.date.today()), 'total_consumption': -2},
    #         {'date': create_date(dt.date.today(), 1), 'total_consumption': 0.0},
    #         {'date': create_date(dt.date.today(), 2), 'total_consumption': 0},
    #                 ]
    #         }
    #           )



#mockito: mock_method: mock bien hecho a json.dump,
#  verify call: Check method has been called
#  Verify + Capture param: Comprobar parametros


if __name__ == "__main__":
    unittest.main()