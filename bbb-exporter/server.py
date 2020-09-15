import logging
import sys
from time import sleep

from prometheus_client import start_http_server, REGISTRY

import settings
from collector import BigBlueButtonCollector
from helpers import verify_recordings_base_dir_exists

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s]: %(message)s")


if __name__ == '__main__':
    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    if settings.RECORDINGS_METRICS_READ_FROM_DISK:
        logging.info("Enabling recordings metrics read from disk, we will not request expensive recordings metrics "
                     "via the API")
        if verify_recordings_base_dir_exists():
            logging.debug("BigBlueButton recordings base dir exists")
        else:
            logging.fatal("BigBlueButton recordings base dir (" + settings.recordings_metrics_base_dir + ") does not " +
                          "exist. Disable RECORDINGS_METRICS_READ_FROM_DISK=true or run on BigBlueButton server.")
            sys.exit(1)

    start_http_server(settings.PORT, addr=settings.BIND_IP)
    logging.info("HTTP server started on {}:{}".format(settings.BIND_IP, settings.PORT))

    collector = BigBlueButtonCollector()

    if len(settings.ROOM_PARTICIPANTS_CUSTOM_BUCKETS) > 0:
        collector.set_room_participants_buckets(settings.ROOM_PARTICIPANTS_CUSTOM_BUCKETS)

    if len(settings.ROOM_LISTENERS_CUSTOM_BUCKETS) > 0:
        collector.set_room_listeners_buckets(settings.ROOM_LISTENERS_CUSTOM_BUCKETS)

    if len(settings.ROOM_VOICE_PARTICIPANTS_CUSTOM_BUCKETS) > 0:
        collector.set_room_voice_participants_buckets(settings.ROOM_VOICE_PARTICIPANTS_CUSTOM_BUCKETS)

    if len(settings.ROOM_VIDEO_PARTICIPANTS_CUSTOM_BUCKETS) > 0:
        collector.set_room_video_participants_buckets(settings.ROOM_VIDEO_PARTICIPANTS_CUSTOM_BUCKETS)

    REGISTRY.register(collector)
    while True:
        sleep(1)
