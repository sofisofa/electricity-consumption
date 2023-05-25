#!/usr/bin/env python3

import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename='/tmp/electricityconsumption.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

class Api:
    """Login on energy provider web and retrieve data."""
    
    def __init__(self, api_info):
        self.token = None
        self.refresh_token = None
        self.login_payload = api_info['login_payload']
        self.login_url = api_info['login_url']
        self.consumption_url = api_info['consumption_url']
        logging.info("Performing Holaluz login")
        self.login()
    
    def login(self):
        
        request_url = self.login_url
        r = requests.post(request_url, data=self.login_payload)
        if r.status_code != 200:
            logging.warning("Holaluz login failed!")
            raise Exception(f"HTTPError: {r.status_code}.")
        else:
            self.token = r.json()['token']
            self.refresh_token = r.json()['refresh_token']
    
    def retrieve_data(self):
        request_url = self.consumption_url
        auth_header = {'Authorization': f'Bearer {self.token}'}

        logging.info("Retrieving data from Holaluz.")
        r = requests.get(request_url, headers=auth_header)
        if r.status_code != 200:
            logging.warning("Data retrieval failed!")
            raise Exception(f'HTTPError: {r.status_code}.')
        else:
            data = r.json()[0]["daily"]
            if len(data) == 0:
                logging.debug("Retrieved Holaluz data but it's empty!")
                raise Exception("Data retrieved but is empty!")
            else:
                return data


# TODO:
#   -implement refresh token

