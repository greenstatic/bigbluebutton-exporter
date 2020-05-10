# Getting Started
First you will need to choose your installation configuration.

## Installation Type Matrix
| Recommended installation type | Number of BBB servers | Existing Prometheus & Grafana services | Do you like Docker? | 
| --- | --- | --- | --- |
| [Docker installation](./installation/bigbluebutton_exporter.md#docker-installation-recommended) (recommended) | multiple | ✅ | ✅ |  
| [All-In-One Monitoring Stack installation](./installation/all_in_one_monitoring_stack.md) | 1 | ❌ | ✅ |
| [Systemd installation](./installation/bigbluebutton_exporter.md#systemd-installation-not-recommended) (not recommended) | multiple | ✅ | ❌ |

If you choose the Docker or Systemd installation type you will have the choice of choosing between node_exporter 
(recommended) and Netdata for server resource utilization metrics.
The metrics that will be collected from one of these two tools will be used together with BigBlueButton exporter metrics
in the _Server Instance_ Grafana dashboards.

[node_exporter installation instructions](./installation/node_exporter.md)

[Netdata installation instructions](./installation/netdata.md)

## Grafana Dashboards
Once you have the BigBlueButton exporter installed and one of the two resource utilization metric exporters (node_exporter
or Netdata), you can import the appropriate Grafana dashboards.

!!! note
    We assume a working Grafana-Prometheus installation.
    If you used the All-In-One Monitoring Stack installation type you are covered since Grafana, Prometheus and node_exporter
    come preconfigured. 

Login to Grafana and in the left menu click on _+ icon -> import_

In the JSON field copy/paste the contents of your desired dashboard

| Dashboard | Prerequisites | Short description |
| --- | --- | --- |
| [All Servers](https://github.com/greenstatic/bigbluebutton-exporter/tree/master/extras/dashboards/all_servers.json) dashboard | BigBlueButton Exporter | BBB metrics for all servers in one dashboard |
| [Server Instance (node_exporter)](https://github.com/greenstatic/bigbluebutton-exporter/tree/master/extras/dashboards/server_instance_node_exporter.json) dashboard | BigBlueButton Exporter, node_exporter | BBB server details combined with node_exporter resource metrics |
| [Server Instance (netdata)](https://github.com/greenstatic/bigbluebutton-exporter/tree/master/extras/dashboards/server_instance_netdata.json) dashboard | BigBlueButton Exporter, Netdata | BBB server details combined with Netdata resource metrics |

### Installing Grafana on the BigBlueButton Server
If you plan to [install Grafana](https://grafana.com/docs/grafana/latest/installation/) on the BigBlueButton host itself, 
keep in mind that the standard port for Grafana (3000) is also used by the html5-client of BigBlueButton 
(see `/etc/bigbluebutton/nginx/bbb-html5.nginx`).
In this case you will need to change the Grafana port in `/etc/grafana/grafana.ini` to something else, e.g. 3001).
