import json
import random
import time

import requests

from settings import BASE_URL, API_KEY


def download_from(endpoint: str) -> dict:
    res = requests.get(endpoint)
    time.sleep(random.uniform(0, 2))
    json_data = json.loads(res.text)
    return json_data


class EndpointBuilder:
    def __init__(self, api_method):
        if BASE_URL is None or API_KEY is None or BASE_URL == "" or API_KEY == "":
            raise ValueError("Must set BASE_URL and API_KEY in settings.py")
        self.base = f"{BASE_URL}&method={api_method}"
        self.param_dict = {}

    def param(self, key, val):
        self.param_dict[key] = val
        return self

    def update_param(self, key, val):
        self.param_dict[key] = val
        return self

    def build(self):
        param_str = "&".join(f"{k}={v}" for k, v in self.param_dict.items())
        return f"{self.base}&{param_str}"
