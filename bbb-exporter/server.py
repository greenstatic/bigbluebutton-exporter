import logging
from time import sleep

from prometheus_client import start_http_server, REGISTRY

import settings
from collector import BigBlueButtonCollector

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s]: %(message)s")


if __name__ == '__main__':
    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    start_http_server(settings.PORT, addr=settings.BIND_IP)
    logging.info("HTTP server started on port: {}".format(settings.PORT))

    REGISTRY.register(BigBlueButtonCollector())
    while True:
        sleep(1)
