#!/bin/python

import requests
import datetime as dt

class HolaLuzClient(): 
    LOGIN_URL = "https://core.holaluz.com/api/private/login_check"
    CONSUMPTION_URL = "https://zc-consumption.holaluz.com/consumption"
    USER = "***REMOVED***"
    PASSWORD = "***REMOVED***"
    LOGIN_REQUEST = {"_app": (None, "customer"), "_username": (None, USER), "_password": (None, PASSWORD) }

    def __init__(self):
        self.session = requests.Session()
        self.login()
    

    def login(self):
        response = requests.post(self.LOGIN_URL, files=self.LOGIN_REQUEST)
        if response.status_code != 200:
            print("Failed with error code {}".format(response.status_code))
    
        self.token = response.json()["token"]
        self.refresh = response.json()["refresh_token"]

    def get_measurements_from_holaluz(self):
        auth_header = {"Authorization" : "Bearer {}".format(self.token)}
        response = requests.request("GET", self.CONSUMPTION_URL, headers=auth_header)
        if response.status_code != 200:
            print("Failed with error code {}".format(response.status_code))
        return response.json()

    
    def format_and_clean_response(self, response_json):
        resp = response_json[0]["daily"]
        return [day for day in resp if dt.date.fromisoformat(day["date"]) < dt.date.today() and day["total_consumption"] != 0.0]


# Continue by adding MQTT to the script and a loop (ideally another script taking care of that)
# Json should be sent to HA and HA can store it in a variable, need to research how to overlap time with the
# one in the JSON. Also, how to manage multiple elements in the same json.
# Improvement: Implement refresh token.
# Maybe check the database for the latest stored date (since postgres should be easily accessible) although this risks a big coupling between both services.
#https://community.home-assistant.io/t/how-to-get-value-from-mqtt-json-to-mqtt-sensor/122774/2
#https://www.home-assistant.io/blog/2015/09/11/different-ways-to-use-mqtt-with-home-assistant/
if __name__ == "main":
    hlc = HolaLuzClient()
    hlc.login()
    resp = hlc.get_measurements_from_holaluz()
    resp_list = hlc.hormat_and_clean_response(resp)
    print(resp_list)