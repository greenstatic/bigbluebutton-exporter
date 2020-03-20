import logging
from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlparse

import xmltodict

import api_lib
import settings


def get_meetings():
    data = api_lib.getMeetings(settings.API_CLIENT)

    if data is None:
        return []

    if data['response']['meetings'] is None:
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

        moderators = []

        if type(meeting['attendees']) == OrderedDict:
            if type(meeting['attendees']['attendee']) == list:
                for attendee in meeting['attendees']['attendee']:
                    if attendee['role'].lower() == "moderator":
                        moderators.append(attendee['fullName'])

            else:
                attendee = meeting['attendees']['attendee']
                if attendee['role'].lower() == 'moderator':
                    moderators.append(attendee['fullName'])

        creation = ""
        try:
            creation = int(datetime.strptime(meeting['createDate'], "%a %b %d %H:%M:%S %Z %Y").timestamp())
        except ValueError:
            logging.error("Failed to parse: " + meeting['createDate'])

        m = {
            "name": meeting['meetingName'],
            "id": meeting['meetingID'],
            "creation": creation,
            "noUsers": meeting['participantCount'],
            "moderators": moderators,
            "metadata": {
                "origin-server": meeting['metadata']['bbb-origin-server-name'],
            }
        }

        # bbb-context is optional in bbb response
        try:
            m['metadata']['origin-context-name'] = _bbb_context_convert_moodle(meeting['metadata']['bbb-context'])
        except KeyError:
            pass

        response.append(m)

    return response


def _bbb_context_convert_moodle(context_html):
    """
        Returns the first inner node string from the context html string (useful for the context string returned
        by the BigBlueButton Moodle plugin.
    """

    context_html = "<root>{}</root>".format(context_html)  # removes the bug where there is no root node in context_html
    return_str = ""

    root = xmltodict.parse(context_html)
    for element in root['root']:
        el = root['root'][element]
        if type(el) == list and len(el) > 0:
            return_str = el[0]['#text']
            break

    return return_str


def about():
    url_parsed = urlparse(settings.API_BASE_URL)

    return {
        "service": "bigbluebutton-exporter",
        "exporterServer": url_parsed.netloc,
        "api": settings.API_BASE_URL,
        "version": settings.VERSION,
        "datetime": datetime.now().isoformat(),
        "source": "https://github.com/greenstatic/bigbluebutton-exporter"}
