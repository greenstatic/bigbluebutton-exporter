import logging
from datetime import datetime
from time import sleep

from prometheus_client import start_http_server

import api
import metrics
import settings

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s]: %(message)s")


if __name__ == '__main__':
    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    start_http_server(settings.PORT)  # TODO - expose this via ENV variable
    logging.info("HTTP server started on port: {}".format(settings.PORT))

    while True:
        logging.debug("Requesting via API meetings data")
        meetings_data_t1 = datetime.now()
        meetings_data = api.get_meetings()
        meetings_data_latency = (datetime.now() - meetings_data_t1).total_seconds()

        logging.debug("Requesting via API recordings processing data")
        recording_processing_data_t1 = datetime.now()
        recording_processing_data = api.get_recordings("processing")
        recording_processing_data_latency = (datetime.now() - recording_processing_data_t1).total_seconds()

        logging.debug("Requesting via API recordings processed data")
        recording_processed_data_t1 = datetime.now()
        recording_processed_data = api.get_recordings("processed")
        recording_processed_data_latency = (datetime.now() - recording_processed_data_t1).total_seconds()

        logging.debug("Requesting via API recordings published data")
        recording_published_data_t1 = datetime.now()
        recording_published_data = api.get_recordings("published")
        recording_published_data_latency = (datetime.now() - recording_published_data_t1).total_seconds()

        logging.debug("Requesting via API recordings unpublished data")
        recording_unpublished_data_t1 = datetime.now()
        recording_unpublished_data = api.get_recordings("unpublished")
        recording_unpublished_data_latency = (datetime.now() - recording_unpublished_data_t1).total_seconds()

        logging.debug("Requesting via API recordings deleted data")
        recording_deleted_data_t1 = datetime.now()
        recording_deleted_data = api.get_recordings("deleted")
        recording_deleted_data_latency = (datetime.now() - recording_deleted_data_t1).total_seconds()

        metrics.process_meetings(meetings_data)
        metrics.process_api_latency("getMeetings", "", meetings_data_latency)

        metrics.process_recordings_processing(recording_processing_data)
        metrics.process_api_latency("getRecordings", "state=processing", recording_processing_data_latency)

        metrics.process_recordings_processed(recording_processed_data)
        metrics.process_api_latency("getRecordings", "state=processed", recording_processed_data_latency)

        metrics.process_recordings_published(recording_published_data)
        metrics.process_api_latency("getRecordings", "state=published", recording_published_data_latency)

        metrics.process_recordings_unpublished(recording_unpublished_data)
        metrics.process_api_latency("getRecordings", "state=unpublished", recording_unpublished_data_latency)

        metrics.process_recordings_deleted(recording_deleted_data)
        metrics.process_api_latency("getRecordings", "state=deleted", recording_deleted_data_latency)

        logging.info("Metrics API scraping completed")
        logging.debug("Sleeping for: {}".format(settings.SLEEP_DURATION))
        sleep(settings.SLEEP_DURATION)
