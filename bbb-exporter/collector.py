import logging
from functools import reduce
from collections import defaultdict

from prometheus_client.metrics_core import GaugeMetricFamily, HistogramMetricFamily
from prometheus_client.utils import INF

import api
import settings
from helpers import execution_duration, HistogramBucketHelper


class BigBlueButtonCollector:
    buckets = [.01, .025, .05, .075, .1, .25, .5, .75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 5.0, 7.5, 10.0, INF]
    histogram_data_meetings_latency = HistogramBucketHelper(buckets)
    histogram_data_recording_processing_latency = HistogramBucketHelper(buckets)
    histogram_data_recording_processed_latency = HistogramBucketHelper(buckets)
    histogram_data_recording_published_latency = HistogramBucketHelper(buckets)
    histogram_data_recording_unpublished_latency = HistogramBucketHelper(buckets)
    histogram_data_recording_deleted_latency = HistogramBucketHelper(buckets)

    def __init__(self):
        pass

    def collect(self):
        logging.info("Collecting metrics from BigBlueButton API")

        logging.debug("Requesting via API meetings data")
        meetings, meetings_data_latency = execution_duration(api.get_meetings)()

        no_meetings = len(meetings)
        no_participants = reduce(lambda total, meeting: total + int(meeting['participantCount']), meetings, 0)
        no_listeners = reduce(lambda total, meeting: total + int(meeting['listenerCount']), meetings, 0)
        no_voice_participants = reduce(lambda total, meeting: total + int(meeting['voiceParticipantCount']), meetings, 0)
        no_video_participants = reduce(lambda total, meeting: total + int(meeting['videoCount']), meetings, 0)
        participants_by_client = self._get_participant_count_by_client(meetings)

        bbb_api_latency = HistogramMetricFamily('bbb_api_latency', "BigBlueButton API call latency",
                                                labels=['endpoint', 'parameters'])
        self.histogram_data_meetings_latency.add(meetings_data_latency)
        bbb_api_latency.add_metric(["getMeetings", ""], self.histogram_data_meetings_latency.get_buckets(),
                                   self.histogram_data_meetings_latency.sum)

        bbb_meetings = GaugeMetricFamily('bbb_meetings', "Number of BigBlueButton meetings")
        bbb_meetings.add_metric([], no_meetings)
        yield bbb_meetings

        bbb_meetings_participants = GaugeMetricFamily('bbb_meetings_participants',
                                                      "Total number of participants in all BigBlueButton meetings")
        bbb_meetings_participants.add_metric([], no_participants)
        yield bbb_meetings_participants

        bbb_meetings_listeners = GaugeMetricFamily('bbb_meetings_listeners',
                                                   "Total number of listeners in all BigBlueButton meetings")
        bbb_meetings_listeners.add_metric([], no_listeners)
        yield bbb_meetings_listeners

        bbb_meetings_voice_participants = GaugeMetricFamily('bbb_meetings_voice_participants',
                                                            "Total number of voice participants in all BigBlueButton "
                                                            "meetings")
        bbb_meetings_voice_participants.add_metric([], no_voice_participants)
        yield bbb_meetings_voice_participants

        bbb_meetings_video_participants = GaugeMetricFamily('bbb_meetings_video_participants',
                                                            "Total number of video participants in all BigBlueButton "
                                                            "meetings")

        bbb_meetings_video_participants.add_metric([], no_video_participants)
        yield bbb_meetings_video_participants

        bbb_meetings_participant_clients = GaugeMetricFamily('bbb_meetings_participant_clients',
                                                            "Total number of participants in all BigBlueButton "
                                                            "meetings by client",
                                                            labels=["type"])
        for client, num in participants_by_client.items():
            bbb_meetings_participant_clients.add_metric([client.lower()], num)
        yield bbb_meetings_participant_clients

        logging.debug("Requesting via API recordings processing data")
        bbb_recordings_processing = GaugeMetricFamily('bbb_recordings_processing',
                                                      "Total number of BigBlueButton recordings processing")
        recording_processing_data, recording_processing_latency = execution_duration(api.get_recordings)("processing")
        bbb_recordings_processing.add_metric([], len(recording_processing_data))
        self.histogram_data_recording_processing_latency.add(recording_processing_latency)
        bbb_api_latency.add_metric(["getRecordings", "state=processing"],
                                   self.histogram_data_recording_processing_latency.get_buckets(),
                                   self.histogram_data_recording_processing_latency.sum)
        yield bbb_recordings_processing

        logging.debug("Requesting via API recordings processed data")
        recordings_processed_data = GaugeMetricFamily('bbb_recordings_processed',
                                                      "Total number of BigBlueButton recordings processed")
        recording_processed_data, recording_processed_latency = execution_duration(api.get_recordings)("processed")
        recordings_processed_data.add_metric([], len(recording_processed_data))
        self.histogram_data_recording_processed_latency.add(recording_processed_latency)
        bbb_api_latency.add_metric(["getRecordings", "state=processed"],
                                   self.histogram_data_recording_processed_latency.get_buckets(),
                                   self.histogram_data_recording_processed_latency.sum)
        yield recordings_processed_data

        logging.debug("Requesting via API recordings published data")
        recordings_published = GaugeMetricFamily('bbb_recordings_published',
                                                 "Total number of BigBlueButton recordings published")
        recording_published_data, recording_published_latency = execution_duration(api.get_recordings)("published")
        recordings_published.add_metric([], len(recording_published_data))
        self.histogram_data_recording_published_latency.add(recording_published_latency)
        bbb_api_latency.add_metric(["getRecordings", "state=published"],
                                   self.histogram_data_recording_published_latency.get_buckets(),
                                   self.histogram_data_recording_published_latency.sum)
        yield recordings_published

        logging.debug("Requesting via API recordings unpublished data")
        recordings_unpublished = GaugeMetricFamily('bbb_recordings_unpublished',
                                                   "Total number of BigBlueButton recordings unpublished")
        recording_unpublished_data, recording_unpublished_latency = execution_duration(api.get_recordings)("unpublished")
        recordings_unpublished.add_metric([], len(recording_unpublished_data))
        self.histogram_data_recording_unpublished_latency.add(recording_unpublished_latency)
        bbb_api_latency.add_metric(["getRecordings", "state=unpublished"],
                                   self.histogram_data_recording_unpublished_latency.get_buckets(),
                                   self.histogram_data_recording_unpublished_latency.sum)
        yield recordings_unpublished

        logging.debug("Requesting via API recordings deleted data")
        recordings_deleted = GaugeMetricFamily('bbb_recordings_deleted',
                                               "Total number of BigBlueButton recordings deleted")
        recording_deleted_data, recording_deleted_latency = execution_duration(api.get_recordings)("deleted")
        recordings_deleted.add_metric([], len(recording_deleted_data))
        self.histogram_data_recording_deleted_latency.add(recording_deleted_latency)
        bbb_api_latency.add_metric(["getRecordings", "state=deleted"],
                                   self.histogram_data_recording_deleted_latency.get_buckets(),
                                   self.histogram_data_recording_deleted_latency.sum)
        yield recordings_deleted

        bbb_api_up = GaugeMetricFamily('bbb_api_up', "1 if BigBlueButton API is responding 0 otherwise")
        bbb_api_up.add_metric([], 1 if settings._api_up else 0)

        yield bbb_api_up
        yield bbb_api_latency

        logging.info("Finished collecting metrics from BigBlueButton API")

    @staticmethod
    def _get_participant_count_by_client(self, meetings):
        p_by_c = defaultdict(int, {'HTML5': 0, 'DIAL-IN': 0, 'FLASH': 0})
        for meeting in meetings:
            if isinstance(meeting['attendees']['attendee'], list):
                attendees = meeting['attendees']['attendee']
            else:
                attendees = [meeting['attendees']['attendee']]

            for attendee in attendees:
                p_by_c[attendee['clientType']] += 1

        return p_by_c
