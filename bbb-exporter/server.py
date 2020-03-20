import logging
from time import sleep

from prometheus_client import start_http_server

import api
import metrics

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    start_http_server(9688)  # TODO - expose this via ENV variable
    logging.info("Starting server")
    while True:
        logging.info("Requesting via API meetings data")
        metrics.process_api_get_meetings(api.get_meetings())
        sleep(5)  # TODO - expose this via ENV variable
