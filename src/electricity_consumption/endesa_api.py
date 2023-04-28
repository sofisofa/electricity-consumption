#!/usr/bin/env python3

import datetime as dt
import json
import os

from EdistribucionAPI import Edistribucion
from dotenv import load_dotenv

load_dotenv()

    
USERNAME = os.getenv('EN_USER')
PW = os.getenv('EN_PASS')


class Endesa:
    
    def __init__(self, user, pw):
        self.edis = Edistribucion(user, pw)
        
    def get_last_consumption_data(self):
        l_cups = self.edis.get_list_cups()[-1]
        l_cups_id = l_cups['Id']
        cycles = self.edis.get_list_cycles(l_cups_id)
        meas = self.edis.get_meas(l_cups_id, cycles[0])
        consumption_data = []
        
        for day in meas:
            day_in_data = []
            for hourly_point in day:
                day_in_data.append(
                    {'date': hourly_point['date'],
                     'hour': hourly_point['hourCCH'],
                     'label': hourly_point['hour'],
                     'consumption': hourly_point['valueDouble']
                     }
                )
            consumption_data.append(day_in_data)
        
        return consumption_data
    
    @staticmethod
    def reformat_data(data):
        new_data = []
        for day in data:
            new_day = []
            for point in day:
                new_point = {}
                raw_date = point['date']
                raw_hour = point['hour']
                new_date = dt.datetime.strptime(raw_date, '%d/%m/%Y')
                new_date = new_date.date()
                new_point['date'] = new_date.isoformat()
                new_hour = dt.time(hour=raw_hour-1)
                new_point['hour'] = new_hour.isoformat('seconds')
                new_point['label'] = point['label']
                new_point['consumption'] = point['consumption']
                new_day.append(new_point)
            new_data.append(new_day)
        return new_data
    
        
def run():
    endesa = Endesa(USERNAME, PW)
    consumption_data = endesa.get_last_consumption_data()
    consumption_data_reform = endesa.reformat_data(consumption_data)
    
    # Get year and month of consumption data
    date = dt.date.fromisoformat(consumption_data_reform[0][0]["date"])
    month = date.strftime("%b")
    year = date.strftime("%y")
    #
    consumption_json = {'creation date': dt.date.isoformat(dt.date.today()),
                        'hourly_consumption': consumption_data}
    
    with open(f"{os.getenv('PATH_TO_CONSUMPTION_FILES')}en_consumption_{month}_{year}.json", 'w+') as f_obj:
        json.dump(consumption_json, f_obj)


if __name__ == "__main__":
    run()
