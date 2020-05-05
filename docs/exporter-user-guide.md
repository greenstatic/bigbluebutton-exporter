# Exporter User Guide

## Environment Variables
* API_SECRET - BigBlueButton API Secret
    * **Required: true**
    * Use `$ bbb-conf --secret` on BigBlueButton server to get secret and Base API url
* API_BASE_URL - BigBlueButton API base URL
    * **Required: true**
    * Example: "https://example.com/bigbluebutton/api/"
    * Trailing slash is required!
    * Make sure you supply the base url **of the API**, often this URL ends in `/api/`
* DEBUG  - Enable debug logging
    * Required: false
    * Default: false
    * Values: &lt;true | false&gt;
* COLLECT_RECORDINGS - Enable collection of recordings data through the API
    * Required: false
    * Default: true
    * Values: &lt;true | false&gt;
* BIND_IP - Which network address to bind the HTTP server of the exporter
    * Required: false
    * Default: 0.0.0.0
* PORT - HTTP port to serve the exporter metrics
    * Required: false
    * Default: 9688
    * Values: &lt;1 - 65535&gt;
    
## Metrics
Gauges:

* bbb_meetings_participants - Total number of participants in all BigBlueButton meetings
* bbb_meetings_listeners - Total number of listeners in all BigBlueButton meetings
* bbb_meetings_voice_participants - Total number of voice participants in all BigBlueButton meetings
* bbb_meetings_video_participants - Total number of video participants in all BigBlueButton meetings
* bbb_meetings_participant_clients(type=<client\>) - Total number of participants in all BigBlueButton meetings by client (html5|dial-in|flash)
* bbb_recordings_processing - Total number of BigBlueButton recordings processing
* bbb_recordings_processed - Total number of BigBlueButton recordings processed
* bbb_recordings_published - Total number of BigBlueButton recordings published
* bbb_recordings_unpublished - Total number of BigBlueButton recordings unpublished
* bbb_recordings_deleted - Total number of BigBlueButton recordings deleted
* bbb_api_up - 1 if BigBlueButton API is responding 0 otherwise

Histograms:

* bbb_api_latency(labels: endpoint, parameters) - BigBlueButton API call latency
    * buckets: .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 5.0, 7.5, 10.0, INF
    