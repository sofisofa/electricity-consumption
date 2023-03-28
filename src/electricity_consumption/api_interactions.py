#!/usr/bin/env python3

import requests
import json
import datetime as dt
import os
from dotenv import load_dotenv

load_dotenv()


class Api:
    """Login on energy provider web and retrieve data."""
    
    def __init__(self, api_info):
        self.token = None
        self.refresh_token = None
        self.login()
        self.login_payload = {'_app': 'customer', '_username': api_info['user'], '_password': api_info['pw']}
        self.login_url = api_info['login_url']
        self.consumption_url = api_info['consumption_url']
    
    def login(self):
        
        request_url = self.login_url
        r = requests.post(request_url, data=self.login_payload)
        if r.status_code != 200:
            raise Exception(f"Login failed! HTTPError: {r.status_code}.")
        else:
            self.token = r.json()['token']
            self.refresh_token = r.json()['refresh_token']
    
    def retrieve_data(self):
        request_url = self.consumption_url
        auth_header = {'Authorization': f'Bearer {self.token}'}
        
        r = requests.get(request_url, headers=auth_header)
        if r.status_code != 200:
            raise Exception(f'Data retrieval failed! HTTPError: {r.status_code}.')
        else:
            data = r.json()[0]["daily"]
            if len(data) == 0:
                raise Exception('Data retrieved but is empty!')
            else:
                return data
    

# TODO:
#   -implement refresh token,


    