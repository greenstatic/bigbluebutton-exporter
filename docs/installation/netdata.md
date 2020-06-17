# Netdata
Follow these instructions in order to view system resource utilization with the `server_instace_netdata.yaml` Grafana dashboard.

Instructions bellow will configure Netdata to bind to localhost and configure Nginx as a reverse proxy that will expose 
Netdata via a location directive with HTTP basic auth.

## Step-by-step Guide
This guide is built upon [https://docs.netdata.cloud/backends/prometheus/](https://docs.netdata.cloud/backends/prometheus/).

### 1. Install Netdata
Follow Netdata's official instruction on how to install Netdata: 
[https://docs.netdata.cloud/packaging/installer/](https://docs.netdata.cloud/packaging/installer/).

### 2. Configure Netdata to bind to localhost
Find the `[web]` section and make sure `bind to = 127.0.0.1`.

```shell
cd /etc/netdata
sudo ./edit-config netdata.conf
```


### 3. Create HTTP basic auth password

!!! info
    For this you will need the handy `apache2-utils` package to create a password that will be used with HTTP basic auth by Nginx.
    You can install it (on Ubuntu) by running: `sudo apt install apache2-utils`.

Create a username (e.g. monitoring) and password.
You will be prompted after you run the `htpasswd` command for the desired password.

!!! tip
    The username and password combo doesn't need to be the same as the one for the exporter.

```shell
# You may replace monitoring with any desired username
# add `-c` flag to create the file if it doesn't exist
sudo htpasswd /etc/nginx/.htpasswd monitoring
```

### 4. Add Nginx site configuration
Add the location directive to your Nginx web server (`/etc/nginx/sites-available/bigbluebutton`) that will proxy traffic to
`127.0.0.1:19999`.

```text
# Netdata metrics
location /netdata/ {
    auth_basic "Netdata Monitoring";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:19999/;
    include proxy_params;
}
```

### 5. Add Netdata to your Prometheus scrape jobs
Add the following job to your Prometheus configuration.
Replace `example.com` with your BigBlueButton's domain.

```yaml
- job_name: 'bbb_netdata'
  metrics_path: '/netdata/api/v1/allmetrics'
  params:
    format: [prometheus]
  honor_labels: true
  scheme: https
  basic_auth:
    username: "<HTTP BASIC AUTH USERNAME>"
    password: "<HTTP BASIC AUTH PASSWORD>"
  static_configs:
  - targets: ['example.com']
``` 

### 6. Import the dashboard to your Grafana
Log into your Grafana web interface, click on `+` -> `Import` and select `Upload .json file`.
Select the file `extras/dashboards/server_instance_netdata.json` from the repository (clone the repository or copy the 
contents of the file).


## Notes
### Multiple BigBlueButton servers
If you wish to monitor multiple BigBlueButton servers simply do steps 1-4 for each server and then add each server's 
domain to the `targets` field in Prometheuses `bbb_netdata` job configuration.

### Setup Netdata without the Nginx reverse proxy
In the case you do not wish to deploy your Netdata behind the Nginx reverse proxy, you either need to fix the 
Server Instance Grafana Dashboard (not recommended) or add a Prometheus relabel config.

Thank you to [@robbi5](https://github.com/robbi5) for providing this snippet:
```yaml
relabel_configs:
- source_labels: ['__address__']
  separator:     ':'
  regex:         '(.*):.*'
  target_label:  'instance'
  replacement:   '$1'
```

See [issue #3](https://github.com/greenstatic/bigbluebutton-exporter/issues/3) for more details.
