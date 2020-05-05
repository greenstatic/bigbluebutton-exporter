# BigBlueButton Exporter
Prometheus exporter for BigBlueButton.
On a HTTP `/metrics` request, the exporter will query the BigBlueButton's API for data which it then aggregates and exposes as metrics.

![Docker Pulls](https://img.shields.io/docker/pulls/greenstatic/bigbluebutton-exporter?logo=Docker)
![Docker Image Version (latest semver)](https://img.shields.io/docker/v/greenstatic/bigbluebutton-exporter?label=latest%20docker%20image&logo=Docker&sort=semver)
![GitHub](https://img.shields.io/github/license/greenstatic/bigbluebutton-exporter)

Docker container image: [https://hub.docker.com/r/greenstatic/bigbluebutton-exporter](https://hub.docker.com/r/greenstatic/bigbluebutton-exporter)

Default port: 9688

## Documentation
Available at: [https://bigbluebutton-exporter.greenstatic.dev](https://bigbluebutton-exporter.greenstatic.dev)

## Grafana Dashboard Screenshot

![](docs/assets/img_grafana_dashboard_server_instance.png)

![](docs/assets/img_grafana_dashboard_server_instance.png)

## Metrics
Gauges:
* bbb_meetings_participants - Total number of participants in all BigBlueButton meetings
* bbb_meetings_listeners - Total number of listeners in all BigBlueButton meetings
* bbb_meetings_voice_participants - Total number of voice participants in all BigBlueButton meetings
* bbb_meetings_video_participants - Total number of video participants in all BigBlueButton meetings
* bbb_meetings_participant_clients(type=<client>) - Total number of participants in all BigBlueButton meetings by client (html5|dial-in|flash)
* bbb_recordings_processing - Total number of BigBlueButton recordings processing
* bbb_recordings_processed - Total number of BigBlueButton recordings processed
* bbb_recordings_published - Total number of BigBlueButton recordings published
* bbb_recordings_unpublished - Total number of BigBlueButton recordings unpublished
* bbb_recordings_deleted - Total number of BigBlueButton recordings deleted
* bbb_api_up - 1 if BigBlueButton API is responding 0 otherwise

Histograms:
* bbb_api_latency(labels: endpoint, parameters) - BigBlueButton API call latency
    * buckets: .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 5.0, 7.5, 10.0, INF
    
## Environment Variables
* API_SECRET - BigBlueButton API Secret
    * **Required: true**
    * Use `$ bbb-conf --secret` on BigBlueButton server to get secret and Base API url
* API_BASE_URL - 
    * **Required: true**
    * Example: "https://example.com/bigbluebutton/api/"
    * Trailing slash is required!
* DEBUG 
    * Required: false
    * Default: false
    * Values: <true | false>
* COLLECT_RECORDINGS
    * Required: false
    * Default: true
    * Values: <true | false>
* BIND_IP
    * Required: false
    * Default: 0.0.0.0
* PORT
    * Required: false
    * Default: 9688
    * Values: <1 - 65535>
    