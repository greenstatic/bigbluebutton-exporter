# Overview of BigBlueButton Exporter
**BigBlueButton Exporter** is a Prometheus exporter for [BigBlueButton](https://bigbluebutton.org/).
On a HTTP `/metrics` request, the exporter will query the BigBlueButton's API for data which it then aggregates and exposes as metrics.

![Docker Pulls](https://img.shields.io/docker/pulls/greenstatic/bigbluebutton-exporter?logo=Docker)
![Docker Image Version (latest semver)](https://img.shields.io/docker/v/greenstatic/bigbluebutton-exporter?label=latest%20docker%20image&logo=Docker&sort=semver)
![GitHub](https://img.shields.io/github/license/greenstatic/bigbluebutton-exporter)


Metrics exposed:

* Number of participants by type (listeners, voice, video)
* Number of participants by client (HTML5, dial-in, flash)
* Number of recordings (processing, published, unpublished, deleted, unprocessed)
* Number of participants in rooms by bucket

## Use Case
BigBlueButton Exporter is the bridge between BigBlueButton and modern monitoring infrastructure such as Prometheus, Alertmanager & Grafana.

Using BigBlueButton Exporter you can create stunning dashboards for your BigBlueButton infrastructure and create alert
rules when certain things happen.

### Multiple BigBlueButton servers dashboard
With this dashboard you have a quick overlook over all your BigBlueButton servers and quickly spot anomalies.

![](assets/img_grafana_dashboard_all_servers.png)

### Single detailed BigBlueButton server dashboard:
This dashboard gives you details about a single BigBlueButton server and it's performance compared to it's resources
(CPU utilization and network bandwidth).

![](assets/img_grafana_dashboard_server_instance.png)

!!! note 
    Additional software is required to display server resources i.e. node_exporter or Netdata.
    We cover this in the installation instructions.
