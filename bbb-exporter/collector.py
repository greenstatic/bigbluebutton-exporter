import logging
import os
from functools import reduce
from collections import defaultdict

from prometheus_client.metrics_core import GaugeMetricFamily, HistogramMetricFamily, GaugeHistogramMetricFamily, \
    CounterMetricFamily
from prometheus_client.utils import INF

import api
import settings
from helpers import execution_duration, HistogramBucketHelper


class BigBlueButtonCollector:
    api_latency_buckets = [.01, .025, .05, .075, .1, .25, .5, .75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 5.0, 7.5, 10.0, INF]
    histogram_data_meetings_latency = HistogramBucketHelper(api_latency_buckets)
    histogram_data_recording_processing_latency = HistogramBucketHelper(api_latency_buckets)
    histogram_data_recording_processed_latency = HistogramBucketHelper(api_latency_buckets)
    histogram_data_recording_published_latency = HistogramBucketHelper(api_latency_buckets)
    histogram_data_recording_unpublished_latency = HistogramBucketHelper(api_latency_buckets)
    histogram_data_recording_deleted_latency = HistogramBucketHelper(api_latency_buckets)

    room_participants_buckets = [0, 1, 5, 15, 30, 60, 90, 120, 150, 200, 250, 300, 400, 500, INF]
    room_listeners_buckets = room_participants_buckets.copy()
    room_voice_participants_buckets = [0, 1, 5, 15, 30, 60, 90, 120, INF]
    room_video_participants_buckets = room_voice_participants_buckets.copy()

    recordings_metrics_base_dir = settings.recordings_metrics_base_dir
    recordings_metrics_from_disk = settings.RECORDINGS_METRICS_READ_FROM_DISK

    last_scrape_meetings = set([])
    unique_meetings_count = 0

    last_scrape_breakout_rooms = set([])
    unique_breakout_rooms_count = 0

    def set_room_participants_buckets(self, buckets):
        assert type(buckets) == list
        assert len(buckets) != 0
        self.room_participants_buckets = buckets + [INF]

    def set_room_listeners_buckets(self, buckets):
        assert type(buckets) == list
        assert len(buckets) != 0
        self.room_listeners_buckets = buckets + [INF]

    def set_room_voice_participants_buckets(self, buckets):
        assert type(buckets) == list
        assert len(buckets) != 0
        self.room_voice_participants_buckets = buckets + [INF]

    def set_room_video_participants_buckets(self, buckets):
        assert type(buckets) == list
        assert len(buckets) != 0
        self.room_video_participants_buckets = buckets + [INF]

    def collect(self):
        logging.info("Collecting metrics from BigBlueButton API")

        logging.debug("Requesting via API meetings data")
        meetings, meetings_data_latency = execution_duration(api.get_meetings)()

        bbb_api_latency = HistogramMetricFamily('bbb_api_latency', "BigBlueButton API call latency",
                                                labels=['endpoint', 'parameters'])
        self.histogram_data_meetings_latency.add(meetings_data_latency)
        bbb_api_latency.add_metric(["getMeetings", ""],
                                   self.histogram_data_meetings_latency.get_buckets(),
                                   self.histogram_data_meetings_latency.sum)

        yield self.metric_meetings(meetings)
        yield self.metric_participants(meetings)
        yield self.metric_meetings_listeners(meetings)
        yield self.metric_meetings_voice_participants(meetings)
        yield self.metric_meetings_video_participants(meetings)

        yield self.metric_meetings_participant_clients(meetings)
        yield self.metric_meetings_participants_origin(meetings)

        if settings.RECORDINGS_METRICS_ENABLE:
            yield self.metric_recordings_unpublished(bbb_api_latency)

            if self.recordings_metrics_from_disk:
                yield self.metric_recordings_processing_from_disk()
                yield self.metric_recordings_published_from_disk()

                # There is a slight race condition here since in order to calculate deleted recordings we need
                # the number of published recordings
                yield self.metric_recordings_deleted_from_disk()

                # This is an additional metric that is only available if recordings_metrics_from_disk is enabled
                # since this data isn't available via the API
                yield self.metric_recordings_unprocessed_from_disk()

            else:
                # Perform expensive API calls - this will increase the latency of the scrape
                yield self.metric_recordings_processing(bbb_api_latency)
                yield self.metric_recordings_published(bbb_api_latency)
                yield self.metric_recordings_deleted(bbb_api_latency)

        yield bbb_api_latency

        bbb_api_up = GaugeMetricFamily('bbb_api_up', "1 if BigBlueButton API is responding 0 otherwise")
        bbb_api_up.add_metric([], 1 if settings._api_up else 0)

        yield bbb_api_up

        yield self.metric_participants_histogram(meetings)
        yield self.metric_listeners_histogram(meetings)
        yield self.metric_voice_participants_histogram(meetings)
        yield self.metric_video_participants_histogram(meetings)

        yield self.metric_unique_meetings_count(meetings)
        yield self.metric_unique_breakout_rooms_count(meetings)

        bbb_exporter = GaugeMetricFamily("bbb_exporter", "BigBlueButton Exporter version", labels=["version"])
        bbb_exporter.add_metric([settings.VERSION], 1)
        yield bbb_exporter

        logging.info("Finished collecting metrics from BigBlueButton API")

    def metric_meetings(self, meetings):
        no_meetings = len(meetings)
        metric = GaugeMetricFamily('bbb_meetings', "Number of BigBlueButton meetings")
        metric.add_metric([], no_meetings)
        return metric

    def metric_participants(self, meetings):
        no_participants = reduce(lambda total, meeting: total + int(meeting['participantCount']), meetings, 0)
        metric = GaugeMetricFamily('bbb_meetings_participants',
                                   "Total number of participants in all BigBlueButton meetings")
        metric.add_metric([], no_participants)
        return metric

    def metric_meetings_listeners(self, meetings):
        no_listeners = reduce(lambda total, meeting: total + int(meeting['listenerCount']), meetings, 0)
        metric = GaugeMetricFamily('bbb_meetings_listeners',
                                   "Total number of listeners in all BigBlueButton meetings")
        metric.add_metric([], no_listeners)
        return metric
    
    def metric_meetings_participants_origin(self, meetings):
        participants_by_origin = self._get_participants_count_by_origin(meetings)
        metric = GaugeMetricFamily('bbb_meetings_participants_origin',
                                   "Total number of participants in all BigBlueButton meetings by origin servername",
                                   labels=["server", "name"])
        for (servername, origin), num in participants_by_origin.items():
            metric.add_metric([servername.lower(), origin.lower()], num)
        return metric

    def metric_meetings_voice_participants(self, meetings):
        no_voice_participants = reduce(lambda total, meeting: total + int(meeting['voiceParticipantCount']), meetings, 0)
        metric = GaugeMetricFamily('bbb_meetings_voice_participants',
                                   "Total number of voice participants in all BigBlueButton meetings")
        metric.add_metric([], no_voice_participants)
        return metric

    def metric_meetings_video_participants(self, meetings):
        no_video_participants = reduce(lambda total, meeting: total + int(meeting['videoCount']), meetings, 0)
        metric = GaugeMetricFamily('bbb_meetings_video_participants',
                                   "Total number of video participants in all BigBlueButton meetings")

        metric.add_metric([], no_video_participants)
        return metric

    def metric_meetings_participant_clients(self, meetings):
        participants_by_client = self._get_participant_count_by_client(meetings)
        metric = GaugeMetricFamily('bbb_meetings_participant_clients',
                                   "Total number of participants in all BigBlueButton meetings by client",
                                   labels=["type"])
        for client, num in participants_by_client.items():
            metric.add_metric([client.lower()], num)
        return metric

    def metric_recordings_processing(self, bbb_api_latency_metric):
        logging.debug("Requesting via API recordings processing data")
        histogram = GaugeMetricFamily('bbb_recordings_processing', "Total number of BigBlueButton recordings processing")
        recording_processing_data, recording_processing_latency = execution_duration(api.get_recordings)("processing")
        histogram.add_metric([], len(recording_processing_data))
        self.histogram_data_recording_processing_latency.add(recording_processing_latency)
        bbb_api_latency_metric.add_metric(["getRecordings", "state=processing"],
                                          self.histogram_data_recording_processing_latency.get_buckets(),
                                          self.histogram_data_recording_processing_latency.sum)

        return histogram

    def metric_recordings_published(self, bbb_api_latency_metric):
        logging.debug("Requesting via API recordings published data")
        metric = GaugeMetricFamily('bbb_recordings_published', "Total number of BigBlueButton recordings published")
        recording_published_data, recording_published_latency = execution_duration(api.get_recordings)("published")
        metric.add_metric([], len(recording_published_data))
        self.histogram_data_recording_published_latency.add(recording_published_latency)
        bbb_api_latency_metric.add_metric(["getRecordings", "state=published"],
                                          self.histogram_data_recording_published_latency.get_buckets(),
                                          self.histogram_data_recording_published_latency.sum)
        return metric

    def metric_recordings_unpublished(self, bbb_api_latency_metric):
        logging.debug("Requesting via API recordings unpublished data")
        metric = GaugeMetricFamily('bbb_recordings_unpublished', "Total number of BigBlueButton recordings unpublished")
        recording_unpublished_data, recording_unpublished_latency = execution_duration(api.get_recordings)("unpublished")
        metric.add_metric([], len(recording_unpublished_data))
        self.histogram_data_recording_unpublished_latency.add(recording_unpublished_latency)
        bbb_api_latency_metric.add_metric(["getRecordings", "state=unpublished"],
                                          self.histogram_data_recording_unpublished_latency.get_buckets(),
                                          self.histogram_data_recording_unpublished_latency.sum)
        return metric

    def metric_recordings_deleted(self, bbb_api_latency_metric):
        logging.debug("Requesting via API recordings deleted data")
        metric = GaugeMetricFamily('bbb_recordings_deleted', "Total number of BigBlueButton recordings deleted")
        recording_deleted_data, recording_deleted_latency = execution_duration(api.get_recordings)("deleted")
        metric.add_metric([], len(recording_deleted_data))
        self.histogram_data_recording_deleted_latency.add(recording_deleted_latency)
        bbb_api_latency_metric.add_metric(["getRecordings", "state=deleted"],
                                          self.histogram_data_recording_deleted_latency.get_buckets(),
                                          self.histogram_data_recording_deleted_latency.sum)
        return metric

    def metric_participants_histogram(self, meetings):
        logging.debug("Calculating room participants histogram")
        histogram = HistogramBucketHelper(self.room_participants_buckets)
        for meeting in meetings:
            histogram.add(int(meeting['participantCount']))

        metric = GaugeHistogramMetricFamily('bbb_room_participants', "BigBlueButton room participants histogram gauge")
        metric.add_metric([], histogram.get_buckets(), histogram.sum)

        return metric

    def metric_listeners_histogram(self, meetings):
        logging.debug("Calculating room listeners histogram")
        histogram = HistogramBucketHelper(self.room_listeners_buckets)
        for meeting in meetings:
            histogram.add(int(meeting['listenerCount']))

        metric = GaugeHistogramMetricFamily('bbb_room_listeners', "BigBlueButton room listeners histogram gauge")
        metric.add_metric([], histogram.get_buckets(), histogram.sum)
        return metric

    def metric_voice_participants_histogram(self, meetings):
        logging.debug("Calculating room voice participants histogram")
        histogram = HistogramBucketHelper(self.room_voice_participants_buckets)
        for meeting in meetings:
            histogram.add(int(meeting['voiceParticipantCount']))

        metric = GaugeHistogramMetricFamily('bbb_room_voice_participants',
                                            "BigBlueButton room voice participants histogram gauge")
        metric.add_metric([], histogram.get_buckets(), histogram.sum)
        return metric

    def metric_video_participants_histogram(self, meetings):
        logging.debug("Calculating room video participants histogram")
        histogram = HistogramBucketHelper(self.room_video_participants_buckets)
        for meeting in meetings:
            histogram.add(int(meeting['videoCount']))

        metric = GaugeHistogramMetricFamily('bbb_room_video_participants',
                                            "BigBlueButton room video participants histogram gauge")
        metric.add_metric([], histogram.get_buckets(), histogram.sum)
        return metric

    def metric_recordings_processing_from_disk(self):
        logging.debug("Querying disk for recordings processing data")
        metric = GaugeMetricFamily('bbb_recordings_processing', "Total number of BigBlueButton recordings processing "
                                                                "(scraped from disk)")
        metric.add_metric([], recordings_processing_from_disk(self.recordings_metrics_base_dir))
        return metric

    def metric_recordings_published_from_disk(self):
        logging.debug("Querying disk for recordings published data")
        metric = GaugeMetricFamily('bbb_recordings_published', "Total number of BigBlueButton recordings published "
                                                               "(scraped from disk)")
        metric.add_metric([], recordings_published_from_disk(self.recordings_metrics_base_dir))
        return metric

    def metric_recordings_deleted_from_disk(self):
        logging.debug("Querying disk for recordings deleted data")
        metric = GaugeMetricFamily('bbb_recordings_deleted', "Total number of BigBlueButton recordings deleted "
                                                             "(scraped from disk)")
        metric.add_metric([], recordings_deleted_from_disk(self.recordings_metrics_base_dir))
        return metric

    def metric_recordings_unprocessed_from_disk(self):
        logging.debug("Querying disk for recordings unprocessed data")
        metric = GaugeMetricFamily('bbb_recordings_unprocessed', "Total number of BigBlueButton recordings enqueued to "
                                                                 "be processed (scraped from disk)")
        metric.add_metric([], recordings_unprocessed_from_disk(self.recordings_metrics_base_dir))
        return metric

    def metric_unique_meetings_count(self, meetings):
        logging.debug("Calculating count of unique non-breakout meetings")

        # Meetings that are not breakout rooms
        m = list(filter(lambda meeting: meeting['isBreakout'].lower() == "false", meetings))

        meetings_2 = set(map(lambda meeting: meeting['internalMeetingID'], m))
        new_meetings_count = len(meetings_2 - self.last_scrape_meetings)
        self.unique_meetings_count += new_meetings_count
        self.last_scrape_meetings = meetings_2

        metric = CounterMetricFamily('bbb_unique_meetings', "Unique non-breakout meetings counter")
        metric.add_metric([], self.unique_meetings_count)
        return metric

    def metric_unique_breakout_rooms_count(self, meetings):
        logging.debug("Calculating count of unique breakout rooms")

        # Meetings that are not breakout rooms
        m = list(filter(lambda meeting: meeting['isBreakout'].lower() == "true", meetings))

        meetings_2 = set(map(lambda meeting: meeting['internalMeetingID'], m))
        new_breakout_meetings_count = len(meetings_2 - self.last_scrape_breakout_rooms)
        self.unique_breakout_rooms_count += new_breakout_meetings_count
        self.last_scrape_breakout_rooms = meetings_2

        metric = CounterMetricFamily('bbb_unique_breakout_rooms', "Unique breakout rooms counter")
        metric.add_metric([], self.unique_breakout_rooms_count)
        return metric

    @staticmethod
    def _get_participant_count_by_client(meetings):
        p_by_c = defaultdict(int, {'HTML5': 0, 'DIAL-IN': 0, 'FLASH': 0})
        for meeting in meetings:
            if not meeting.get("attendees"):
                continue
            if isinstance(meeting['attendees']['attendee'], list):
                attendees = meeting['attendees']['attendee']
            else:
                attendees = [meeting['attendees']['attendee']]

            for attendee in attendees:
                p_by_c[attendee['clientType']] += 1

        return p_by_c

    @staticmethod
    def _get_participants_count_by_origin(meetings):
        p_by_m = defaultdict(int)
        for meeting in meetings:
            participants = int(meeting['participantCount'])
            if participants == 0:
                continue
            key = ('', '')
            if meeting.get("metadata"):
                servername = meeting['metadata'].get('bbb-origin-server-name') or ''
                origin = meeting['metadata'].get('bbb-origin') or ''
                key = (servername, origin)
            p_by_m[key] += participants
        return p_by_m


def recordings_processing_from_disk(bigbluebutton_base_dir) -> int:
    # bigbluebutton_base_dir i.e. "/var/bigbluebutton/"
    path = os.path.join(bigbluebutton_base_dir, "recording/process/presentation")
    try:
        return len(os.listdir(path=path))
    except FileNotFoundError:
        logging.info("Path %s doesn't exist, setting processing recordings to 0", path)
        return 0


def recordings_published_from_disk(bigbluebutton_base_dir) -> int:
    # bigbluebutton_base_dir i.e. "/var/bigbluebutton/"
    path = os.path.join(bigbluebutton_base_dir, "published/presentation")
    try:
        return len(os.listdir(path=path))
    except FileNotFoundError:
        logging.info("Path %s doesn't exist, setting published recordings to 0", path)
        return 0


def recordings_deleted_from_disk(bigbluebutton_base_dir) -> int:
    # bigbluebutton_base_dir i.e. "/var/bigbluebutton/"
    path = os.path.join(bigbluebutton_base_dir, "recording/status/published")
    try:
        return len(os.listdir(path=path)) - recordings_published_from_disk(bigbluebutton_base_dir)
    except FileNotFoundError:
        logging.info("Path %s doesn't exist, setting deleted recordings to 0", path)
        return 0


def recordings_unprocessed_from_disk(bigbluebutton_base_dir) -> int:
    # bigbluebutton_base_dir i.e. "/var/bigbluebutton/"
    path = os.path.join(bigbluebutton_base_dir, "recording/status/sanity")
    try:
        return len(os.listdir(path=path))
    except FileNotFoundError:
        logging.info("Path %s doesn't exist, setting unprocessed recordings to 0", path)
        return 0
