import collections
import hashlib
import logging
from typing import Optional
from urllib.parse import urljoin

import requests
import xmltodict as xmltodict

import settings


class Client:
    """
    tls_verify: can either be a boolean (True/False) to enable/disable TLS CA verification or
                a string that contains the path to a CA_BUNDLE file or directory.
                See: https://2.python-requests.org/en/master/user/advanced/#ssl-cert-verification
    """

    def __init__(self, base_url: str, secret: str, tls_verify):
        self.base_url = base_url
        self.secret = secret
        self.tls_verify = tls_verify


def api_get_call(endpoint: str, client: Client, params={}) -> Optional[collections.OrderedDict]:
    if client.tls_verify is False:
        logging.info("TLS CA verification has been disabled for API call")
    elif type(client.tls_verify) == str:
        logging.info("Using custom TLS CA_BUNDLE path (%s) for API call", client.tls_verify)
    else:
        logging.debug("TLS CA verification is enabled for API call")

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
        r = requests.get(url, verify=client.tls_verify)
    except Exception as e:
        logging.error("Failed to perform API call")
        logging.error(e)
        settings._api_up = False
        return None

    if int(r.status_code / 100) != 2:
        logging.error("Non 2xx HTTP status code response")
        logging.error(r.text)
        settings._api_up = False
        return None

    if settings.DEBUG:
        print(r.text)

    try:
        data = xmltodict.parse(r.text)
        if data['response']['returncode'].lower() != "success":
            logging.error("Recieved a non-success response: " + data['response']['message'])
            return None

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
