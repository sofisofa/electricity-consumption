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
        for day in data:
            if dt.date.fromisoformat(day['date']) > dt.date.today() and day["total_consumption"] == 0.0:
                del day
    
        return data
    

def month_from_num(num):
    """Retrieve month of measurements from a number from 1 to 12"""    
    switcher = {
        1: 'january',
        2: 'february',
        3: 'march',
        4: 'april',
        5: 'may',
        6: 'june',
        7: 'july',
        8: 'august',
        9: 'september',
        10: 'october', 
        11: 'november',
        12 : 'december'
    }    
    try :
        month = switcher[num]
    except KeyError:
        print('Invalid month!')
    return month


if __name__ == "__main__":
    hl = HolaLuz()
    data = hl.retrieve_data()
    data = hl.clean_data(data)
    
    #Get year and month of "data"
    date = dt.date.fromisoformat(data[0]["date"])
    num_month = date.month
    month = month_from_num(num_month)
    year = date.year
    
    with open(f'consumption_{month}_{year}.json', 'a') as f_obj:
        json.dump(data,f_obj)