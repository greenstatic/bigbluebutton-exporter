from prometheus_client import Gauge


BBB_MEETINGS = Gauge('bbb_meeting_users', 'BigBlueButton meeting number of users',
                     ['id',
                      'name',
                      'creation',
                      'originServer',
                      'originContextName'])


def process_api_get_meetings(meetings):
    for meeting in meetings:
        origin_context_name = ""
        try:
            origin_context_name = meeting['origin-context-name']
        except KeyError:
            pass

        BBB_MEETINGS.labels(id=meeting['id'],
                            name=meeting['name'],
                            creation=meeting['creation'],
                            originServer=meeting['metadata']['origin-server'],
                            originContextName=origin_context_name).set(meeting['noUsers'])

