from functools import reduce

from prometheus_client import Gauge, Histogram
from prometheus_client.utils import INF

# Metrics
BBB_MEETINGS = Gauge('bbb_meetings', "Number of BigBlueButton meetings")
BBB_MEETINGS_PARTICIPANTS = Gauge('bbb_meetings_participants',
                                  "Total number of participants in all BigBlueButton meetings")
BBB_MEETINGS_LISTENERS = Gauge('bbb_meetings_listeners', "Total number of listeners in all BigBlueButton meetings")
BBB_MEETINGS_VOICE_PARTICIPANTS = Gauge('bbb_meetings_voice_participants',
                                        "Total number of voice participants in all BigBlueButton meetings")
BBB_MEETINGS_VIDEO_PARTICIPANTS = Gauge('bbb_meetings_video_participants',
                                        "Total number of video participants in all BigBlueButton meetings")
BBB_RECORDINGS_PROCESSING = Gauge('bbb_recordings_processing', "Total number of BigBlueButton recordings processing")
BBB_RECORDINGS_PROCESSED = Gauge('bbb_recordings_processed', "Total number of BigBlueButton recordings processed")
BBB_RECORDINGS_PUBLISHED = Gauge('bbb_recordings_published', "Total number of BigBlueButton recordings published")
BBB_RECORDINGS_UNPUBLISHED = Gauge('bbb_recordings_unpublished', "Total number of BigBlueButton recordings unpublished")
BBB_RECORDINGS_DELETED = Gauge('bbb_recordings_deleted', "Total number of BigBlueButton recordings deleted")
BBB_API_LATENCY = Histogram('bbb_api_latency', "Last BigBlueButton API call latency", ['endpoint', 'parameters'],
                            buckets=(.01, .025, .05, .075, .1, .25, .5, .75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 5.0, 7.5,
                                     10.0, INF))
BBB_API_UP = Gauge('bbb_api_up', "1 if BigBlueButton API is responding 0 otherwise")


def process_meetings(meetings):
    """ Meetings is a list of OrderedDict's containing the meeting's data (return value of api.get_meetings()) """

    no_meetings = len(meetings)
    no_participants = reduce(lambda total, meeting: total + int(meeting['participantCount']), meetings, 0)
    no_listeners = reduce(lambda total, meeting: total + int(meeting['listenerCount']), meetings, 0)
    no_voice_participants = reduce(lambda total, meeting: total + int(meeting['voiceParticipantCount']), meetings, 0)
    no_video_participants = reduce(lambda total, meeting: total + int(meeting['videoCount']), meetings, 0)

    BBB_MEETINGS.set(no_meetings)
    BBB_MEETINGS_PARTICIPANTS.set(no_participants)
    BBB_MEETINGS_LISTENERS.set(no_listeners)
    BBB_MEETINGS_VOICE_PARTICIPANTS.set(no_voice_participants)
    BBB_MEETINGS_VIDEO_PARTICIPANTS.set(no_video_participants)


def process_recordings_processing(recordings):
    """ Recordings is a list of OrderedDict's containing the recording's data (return value of api.get_recordings() """
    BBB_RECORDINGS_PROCESSING.set(len(recordings))


def process_recordings_processed(recordings):
    """ Recordings is a list of OrderedDict's containing the recording's data (return value of api.get_recordings() """
    BBB_RECORDINGS_PROCESSED.set(len(recordings))


def process_recordings_published(recordings):
    """ Recordings is a list of OrderedDict's containing the recording's data (return value of api.get_recordings() """
    BBB_RECORDINGS_PUBLISHED.set(len(recordings))


def process_recordings_unpublished(recordings):
    """ Recordings is a list of OrderedDict's containing the recording's data (return value of api.get_recordings() """
    BBB_RECORDINGS_UNPUBLISHED.set(len(recordings))


def process_recordings_deleted(recordings):
    """ Recordings is a list of OrderedDict's containing the recording's data (return value of api.get_recordings() """
    BBB_RECORDINGS_DELETED.set(len(recordings))


def process_api_latency(endpoint:str, parameters:str, latency:float):
    BBB_API_LATENCY.labels(endpoint=endpoint, parameters=parameters).observe(latency)


def process_api_up(api_up: bool):
    BBB_API_UP.set(1 if api_up else 0)
