import json
import logging
from hl_api_interactions import Api
import datetime as dt
import os
from dotenv import load_dotenv

load_dotenv()


class HolaLuz:
    """Login on Holaluz web, clean and store data."""
    
    USERNAME = os.getenv('HL_USER')
    PW = os.getenv('HL_PASS')
    LOGIN_URL = 'https://core.holaluz.com/api/private/login_check'
    CONSUMPTION_URL = 'https://zc-consumption.holaluz.com/consumption'
    LOGIN_PAYLOAD = {'_app': 'customer', '_username': USERNAME, '_password': PW}
    HL_API_INFO = {
        'user': USERNAME,
        'pw': PW,
        'login_url': LOGIN_URL,
        'consumption_url': CONSUMPTION_URL,
        'login_payload': LOGIN_PAYLOAD
    }

    def __init__(self):
        self.api = Api(self.HL_API_INFO)
    
    @staticmethod
    def clean_data(data):
        """Supposing data as retrieved from holaluz, delete elements with 0 consumption (days not measured)"""
        return [day for day in data
                if dt.date.fromisoformat(day['date']) <= dt.date.today() and
                day["total_consumption"] != 0.0
                ]


def run():
    logger = logging.getLogger(__name__)
    hl = HolaLuz()
    consumption_data = hl.api.retrieve_data()
    cleaned_data = hl.clean_data(consumption_data)
    
    # Get year and month of "data"
    date = dt.date.fromisoformat(cleaned_data[0]["date"])
    month = date.strftime("%b")
    year = date.strftime("%y")
    
    # month = date.month
    # year = date.year
    
    cleaned_consumption_json = {'creation date': dt.date.isoformat(dt.date.today()),
                                'daily_consumption': cleaned_data}

    logger.info("Dumping Holaluz data into JSON.")
    with open(f"{os.getenv('PATH_TO_CONSUMPTION_FILES')}hl_consumption_{month}_{year}.json", 'w+') as f_obj:
        json.dump(cleaned_consumption_json, f_obj)


if __name__ == "__main__":
    run()

