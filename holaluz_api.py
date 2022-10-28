import requests
import json
import datetime as dt

class HolaLuz():
    """Login on energy provider web and retrieve data."""

    USERNAME = 'pippo'
    PW = 'password'
    LOGIN_URL = 'https://core.holaluz.com/api/private/login_check'
    CONSUMPTION_URL = 'https://zc-consumption.holaluz.com/consumption'
    LOGIN_PAYLOAD = {'_app': 'customer', '_username' : USERNAME, '_password' : PW}
    
    def __init__(self):
        self.token = None
        self.refresh_token = None
        self.login()

    def login(self):
        request_url = self.LOGIN_URL
        r = requests.post(request_url, data = self.LOGIN_PAYLOAD)
        if r.status_code != 200:
            raise Exception(f"Login failed! HTTPError: {r.status_code}.")
        else:
            self.token = r.json()['token']
            self.refresh_token = r.json()['refresh_token']

    def retrieve_data(self):
        request_url = self.CONSUMPTION_URL
        auth_header = {'Authorization': f'Bearer{self.token}'}
        r = requests.get(request_url, auth_header)
        if r.status_code != 200:
            raise Exception(f'Data retrieval failed! HTTPError: {r.status_code}.')
        else:
            data = r.json()["daily"]
            return data

    def clean_data(data):
        """Supposing JSON file as the one retrieved from holaluz, delete elements with 0 consumption (days not measured)"""
        return [day for day in data if dt.date.fromisoformat(day['date']) <= dt.date.today() and day["total_consumption"] != 0.0]
    

#TODO: 
#   -implement refresh token, 
#   -some way of getting data automatically at end of month

def run():
    hl = HolaLuz()
    data = hl.retrieve_data()
    data = hl.clean_data(data)
    
    #Get year and month of "data"
    date = dt.date.fromisoformat(data[0]["date"])
    month = date.strftime("%b")
    year = date.strftime("%y")

    #month = date.month
    #year = date.year
    
    with open(f'consumption_{month}_{year}.json', 'a') as f_obj:
        json.dump(data,f_obj)

if __name__ == "__main__":
    run()