import collections
import hashlib
import logging
from typing import Optional
from urllib.parse import urljoin

import requests
import xmltodict as xmltodict

import settings


class Client:
    def __init__(self, base_url: str, secret: str):
        self.base_url = base_url
        self.secret = secret


def api_get_call(endpoint: str, client: Client, params={}) -> Optional[collections.OrderedDict]:
    url_params_partial = []
    for key, value in params.items():
        url_params_partial.append("{}={}".format(key, value))

    param_str = "&".join(url_params_partial)

    plaintext = endpoint + param_str + client.secret
    sha1 = hashlib.sha1()
    sha1.update(plaintext.encode('utf-8'))
    checksum = sha1.hexdigest()

    param_str2 = ""
    if param_str != "":
        param_str2 = "&" + param_str
    url = urljoin(client.base_url, endpoint + "?checksum=" + checksum + param_str2)

    try:
        r = requests.get(url)
    except Exception as e:
        logging.error("Failed to perform API call")
        logging.error(e)
        settings._api_up = False
        return None

    try:
        data = xmltodict.parse(r.text)
        settings._api_up = True
        return data
    except Exception as e:
        logging.error("Failed to parse response")
        logging.error(e)
        settings._api_up = False
        return None


def getMeetings(client: Client) -> Optional[collections.OrderedDict]:
    return api_get_call("getMeetings", client)


def getRecordings(client: Client, state: str) -> Optional[collections.OrderedDict]:
    return api_get_call("getRecordings", client, params={"state": state})
