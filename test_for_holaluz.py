import unittest
import responses
import requests
from holaluz_api import HolaLuz

class HolaluzTestCase(unittest.TestCase):
    
    # @responses.activate
    # def test_holaluz_login(self):
        
    #     resp = responses.post("https://example.com", "status" : 200, json = {"token": "token", "refresh_token" : "refresh_token"})

        
    #     self.assertIn()
    def test(self):
        self.assertEqual(5,5)


if __name__ == "__main__":
    unittest.main()