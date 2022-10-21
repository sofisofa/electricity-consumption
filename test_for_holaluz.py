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
        responses.post(
            "https://core.holaluz.com/api/private/login_check",
            status = 404
              )

        hl = HolaLuz()
        
        self.assertIsNone(hl.token)



if __name__ == "__main__":
    unittest.main()