# node_exporter
Follow these instructions in order to view system resource utilization with the 
`extras/dashboards/server_instace_node_exporter.json` Grafana dashboard.

Instructions bellow will configure node_exporter to bind to localhost and configure Nginx as a reverse proxy that will expose 
node_exporter via a location directive with HTTP basic auth.

## Step-by-step Guide
`node_exporter` should be installed on your BigBlueButton server in order to expose system metrics for your Grafan 
dashboards.

### 1. Copy `extras/node_exporter`
```shell
git clone https://github.com/greenstatic/bigbluebutton-exporter.git
cp -r bigbluebutton-exporter/extras/node_exporter ~/
```
!!! tip
    Always check for the latest stable docker image tag (for the `docker-compose.yaml` file). 

### 2. Start using docker-compose
```shell
cd ~/node_exporter
sudo docker-compose up -d
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
`127.0.0.1:9100`.

```text
# node_exporter metrics
location /node_exporter/ {
    auth_basic "node_exporter";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:9100/;
    include proxy_params;
}
```

### 5. Add node_exporter to your Prometheus scrape jobs
Add the following job to your Prometheus configuration.
Replace `example.com` with your BigBlueButton's domain.

```yaml
- job_name: 'bbb_node_exporter'
  metrics_path: '/node_exporter/metrics'
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
Select the file `extras/dashboards/server_instance_node_exporter.json` from the repository (clone the repository or 
copy the contents of the file).


## Notes
### Multiple BigBlueButton servers
If you wish to monitor multiple BigBlueButton servers simply do steps 1-4 for each server and then add each server's 
domain to the `targets` field in Prometheuses `bbb_node_exporter` job configuration.
