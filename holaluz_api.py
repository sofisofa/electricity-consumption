import requests
import json
import datetime as dt

class HolaLuz():
    """Login on energy provider web and retrieve data."""

    USERNAME = 'USERNAME'
    PW = 'PASSWORD'
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
        auth_header = {'Authorization': f'Bearer {self.token}'}
        
        r = requests.get(request_url, headers=auth_header)
        if r.status_code != 200:
            raise Exception(f'Data retrieval failed! HTTPError: {r.status_code}.')
        else:
            data = r.json()[0]["daily"]
            return data

    @staticmethod
    def clean_data(data):
        """Supposing JSON file as the one retrieved from holaluz, delete elements with 0 consumption (days not measured)"""
        return [day for day in data
                if dt.date.fromisoformat(day['date']) <= dt.date.today() and
                day["total_consumption"] != 0.0
                ]
    

#TODO: 
#   -implement refresh token, 
#   -some way of getting data automatically at end of month

def run():
    hl = HolaLuz()
    consumption_data = hl.retrieve_data()
    cleaned_data = hl.clean_data(consumption_data)
    
    #Get year and month of "data"
    date = dt.date.fromisoformat(cleaned_data[0]["date"])
    month = date.strftime("%b")
    year = date.strftime("%y")

    #month = date.month
    #year = date.year
    
    cleaned_consumption_json = {'creation date'  : dt.date.isoformat(dt.date.today()),
                             'daily_consumption' : cleaned_data}
    
    with open(f'.\consumption_files\consumption_{month}_{year}.json', 'w') as f_obj:
        json.dump(cleaned_consumption_json,f_obj)

if __name__ == "__main__":
    run()