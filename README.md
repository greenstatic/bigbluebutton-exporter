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

![](docs/assets/img_grafana_dashboard_all_servers.png)

![](docs/assets/img_grafana_dashboard_server_instance.png)

## Metrics
See: [Exporter User Guide - Metrics](https://bigbluebutton-exporter.greenstatic.dev/exporter-user-guide/#metrics).

## Environment Variables
See: [Exporter User Guide - Environment Variables](https://bigbluebutton-exporter.greenstatic.dev/exporter-user-guide/#environment-variables).
