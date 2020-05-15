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

## Debugging All-In-One Monitoring Stack
### Check Logs
```shell
cd ~/bbb-monitoring
sudo docker-compose logs bbb-exporter
sudo docker-compose logs prometheus
sudo docker-compose logs grafana
sudo docker-compose logs node_exporter

# or skip the service name to view logs for all containers
sudo docker-compose logs
```
### Checking if Prometheus is Scraping Correctly
If you are not receiving any values in Grafana and the container logs do not give
you any hints, it is a good idea to check if Prometheus is scraping any metrics.

Since Prometheus is running on the host's network stack but binded to `127.0.0.1`
we can use SSH to perform a local port forward.
```shell
ssh -NL 9090:127.0.0.1:9090 <HOST>
```

Now visit `http://localhost:9090` on your local machine and the Prometheus web 
interface should appear.
Under `Status` select `Targets`.
Here the `bbb_node_exporter` target should be `up`.

If the target is `down` then there is a scraping issue, if it is `up` then the 
issue is on the Grafana -> Prometheus side.
