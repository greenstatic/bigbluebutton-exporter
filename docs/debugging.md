# Debugging
You might encounter some strange or unexpected metrics from your BigBlueButton server(s).
In order to properly debug the issue it is crucial to figure out where the issue lies;
in the monitoring infrastructure (BigBlueButton Exporter, Prometheus, Grafana, node_exporter, 
Netdata, etc.) or in the BigBlueButton infrastructure.


## Debugging Faulty Metrics
If you suspect there is an issue within BigBlueButton Exporter or the accompanied Grafana 
dashboards you can run the exporter in debug mode and view the XML API response the 
exporter fetches from BigBlueButton.
If the "faulty" metric is contained within the XML API response then the issue lies with
BigBlueButton, otherwise the issue lies within the monitoring stack (BigBlueButton Exporter, 
Prometheus, Grafana, node_exporter, Netdata, etc.).

You can turn on debugging mode, as specified in the 
[Exporter User Guide](./exporter-user-guide.md#environment-variables), by adding the 
environment variable `DEBUG=true`.
This should spit out the XML API responses of all API queries to stdout.
