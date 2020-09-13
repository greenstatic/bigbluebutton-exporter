import logging
from collections import OrderedDict

import api_lib
import settings


def get_meetings():
    data = api_lib.getMeetings(settings.API_CLIENT)

    if data is None:
        return []
    elif 'meetings' not in data['response']:
        return []
    elif data['response']['meetings'] is None:
        return []

    meetings = []
    try:
        if type(data['response']['meetings']['meeting']) == list:
            meetings = data['response']['meetings']['meeting']
        else:
            meetings.append(data['response']['meetings']['meeting'])
    except KeyError:
        logging.warning("Failed to parse meetings")
    except TypeError:
        return []

    response = []

    for meeting in meetings:
        if type(meeting) != OrderedDict:
            continue

        response.append(meeting)

    return response


def get_recordings(state: str):
    data = api_lib.getRecordings(settings.API_CLIENT, state)

    if data is None:
        return []

    if data['response']['recordings'] is None:
        return []

    recordings = []
    try:
        if type(data['response']['recordings']['recording']) == list:
            recordings = data['response']['recordings']['recording']
        else:
            recordings.append(data['response']['recordings']['recording'])
    except KeyError:
        logging.warning("Failed to parse recordings")
    except TypeError:
        return []

    response = []

    for recording in recordings:
        if type(recording) != OrderedDict:
            continue

        response.append(recording)

    return response

