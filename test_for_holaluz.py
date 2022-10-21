import unittest
import responses
import requests
from holaluz_api import HolaLuz

class HolaluzTestCase(unittest.TestCase):
    
    @responses.activate
    def test_holaluz_login(self):
        # Given
        responses.post(
            "https://core.holaluz.com/api/private/login_check",
              json = {
                "token": "token",
                 "refresh_token" : "refresh_token"
                 }
              )

        # When
        hl = HolaLuz()
        # Then
        self.assertEqual(hl.token, "token")

    @responses.activate
    def test_holaluz_failed_login(self):
        expected_error_code = 404
        responses.post(
            "https://core.holaluz.com/api/private/login_check",
            status = expected_error_code
              )

        with self.assertRaises(Exception) as cm:
            HolaLuz()

        the_exception = cm.exception
        self.assertTrue(f"{expected_error_code}" in str(the_exception))



if __name__ == "__main__":
    unittest.main()