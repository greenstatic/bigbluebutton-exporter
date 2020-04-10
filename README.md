# BigBlueButton Exporter
Prometheus exporter for BigBlueButton.
On a HTTP `/metrics` request, the exporter will query the BigBlueButton's API for data which it then aggregates and exposes as metrics.

![Docker Pulls](https://img.shields.io/docker/pulls/greenstatic/bigbluebutton-exporter?logo=Docker)
![Docker Image Version (latest semver)](https://img.shields.io/docker/v/greenstatic/bigbluebutton-exporter?label=latest%20docker%20image&logo=Docker&sort=semver)
![GitHub](https://img.shields.io/github/license/greenstatic/bigbluebutton-exporter)

Docker container image: [https://hub.docker.com/r/greenstatic/bigbluebutton-exporter](https://hub.docker.com/r/greenstatic/bigbluebutton-exporter)

Default port: 9688
## Grafana Dashboard
To import the customized dashboards, select the create button on the left hand side of Grafana and select __import__ then copy/paste the contents of the dashboard's JSON (see bellow for the path of the file).

### Server Instance Dashboard
Using the instance variable (top left corner) one can select a specific BigBlueButton server and view detailed metrics.
**Netdata is required** to view CPU & network bandwidth data.
See [Using Netdata with Prometheus](https://docs.netdata.cloud/backends/prometheus/) for details on how to set it up.

Dashboard is available at: `extras/grafana_dashboard_server_instance.json`

![](extras/img_grafana_dashboard_server_instance.png)

### All Servers Dashboard
Shows aggregated data for all BigBlueButton servers.
Netdata is NOT required for this dashboard.

Dashboard is available at: `extras/grafana_dashboard_all_servers.json`

![](extras/img_grafana_dashboard_all_servers.png)

## Installation
The following instructions will instruct you how to install bbb-exporter on your BigBlueButton server and
direct `/metrics/` to expose your BBB server's metrics.
We assume you have a working installation of BigBlueButton with Nginx as the reverse proxy.

1. On your BigBlueButton server create directory bbb-exporter: 
   ```bash
   $ mkdir ~/bbb-exporter
   ```
1. Copy `extras/docker-compose.yml` to your BigBlueButton server to `~/bbb-exporter/docker-compose.yml`
1. Create the file `~/bbb-exporter/secrets.env` and enter the following
    ```
    # The following information can be found by running: bbb-conf --secret
    # Base URL has /api/ trailing the URL parameter returned by bbb-conf --secret, eg. https://example.com/bigbluebutton/api/
    API_BASE_URL=<BigBlueButton API URL>
    API_SECRET=<BigBlueButton secret>
    ```
1. Start the container:
    ```bash
    # You can replease `latest` with a docker image tag, check docker hub for available tags, link is above.
    $ sudo BBB_EXPORTER_VERSION=latest docker-compose up -d
    ```
1. Add a location directive to your Nginx web server (/etc/nginx/sites-available/bigbluebutton), example is bellow:
    ```
    # BigBlueButton Exporter (metrics)
    location /metrics/ {
      proxy_pass         http://127.0.0.1:9688/;
      proxy_redirect     default;
      proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
      client_max_body_size       10m;
      client_body_buffer_size    128k;
      proxy_connect_timeout      90;
      proxy_send_timeout         90;
      proxy_read_timeout         90;
      proxy_buffer_size          4k;
      proxy_buffers              4 32k;
      proxy_busy_buffers_size    64k;
      proxy_temp_file_write_size 64k;
      include    fastcgi_params;
    }
    ```
1. Reload Nginx: `sudo systemctl reload nginx`
1. Try accessing `/metrics` on your web server
1. You are now ready to add your exporter to your Prometheus configuration, example bellow:
    ```
    - job_name: 'bbb'
      scrape_interval: 5s
      scheme: https
      static_configs:
      - targets: ['bbb.example.com', 'bbb2.example.com']
    ``` 
1. Setup HTTP Basic Auth, see the [HTTP Basic Auth](#http-basic-auth) section for further instructions.
   HTTP Basic Auth is required because each request to the `/metrics` endpoint performs an API call to BigBlueButton which takes a couple of seconds. 
   If exposed to the public internet it could potentially lead to DOS attacks.

### Netdata
If you wish to use the Server Instance Grafana Dashboard, Netdata is required. 
Instructions bellow will configure Netdata to bind to localhost and configure Nginx as a reverse proxy that will expose Netdata via a location directive.

1. Instructions on how to install Netdata can be found: [https://docs.netdata.cloud/packaging/installer/](https://docs.netdata.cloud/packaging/installer/)
1. After you install Netdata, change Netdata's configuration to bind to the address `127.0.0.1`.
    ```bash
    cd /etc/netdata
    sudo ./edit-config netdata.conf

    # Find: [web]
    # then make sure: `bind to = 127.0.0.1` 
    ```
1. To your Nginx configuration (/etc/nginx/sites-available/bigbluebutton) add a location directive, example is bellow:
    ```
    # Netdata Monitoring
    location /netdata/ {
        proxy_pass         http://127.0.0.1:19999/;
        proxy_redirect     default;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        client_max_body_size       10m;
        client_body_buffer_size    128k;
        proxy_connect_timeout      90;
        proxy_send_timeout         90;
        proxy_read_timeout         90;
        proxy_buffer_size          4k;
        proxy_buffers              4 32k;
        proxy_busy_buffers_size    64k;
        proxy_temp_file_write_size 64k;
        include    fastcgi_params;
    }
    ```

1. Then follow the instruction on how to configure Prometheus to scape your Netdata metrics: [https://docs.netdata.cloud/backends/prometheus/](https://docs.netdata.cloud/backends/prometheus/). For your metrics path use: `/netdata/api/v1/allmetrics` (the netdata prefix must be the same as the location path you specified in the Nginx configuration).

    Example Prometheus config bellow:
    ```
    - job_name: 'bbb_netdata'
      metrics_path: '/netdata/api/v1/allmetrics'
      params:
        format: [prometheus]
      honor_labels: true
      scheme: https
      static_configs:
      - targets: ['bbb.example.com', 'bbb2.example.com']
    ``` 

It is strongly recommended to add HTTP Basic Auth to your Nginx location directive.
See the [HTTP Basic Auth](#http-basic-auth) section for instructions.

#### Explanation 
The Server Instance Grafana Dashboard makes the assumption that the instance variable (FQDN + port) is the same for the exporter and Netdata.
This is possible only if they are both behind the Nginx reverse proxy.
This is also the recommended setup, along with HTTP Basic Auth for improved security.

#### Setup Netdata without the Nginx reverse proxy
In the case you do not wish to deploy your Netdata behind the Nginx reverse proxy, you either need to fix the Server Instance Grafana Dashboard (not recommended) or add a Prometheus relabel config.

Thank you to @robbi5 for providing this snippet:
```
relabel_configs:
- source_labels: ['__address__']
  separator:     ':'
  regex:         '(.*):.*'
  target_label:  'instance'
  replacement:   '$1'
```

See [issue #3](https://github.com/greenstatic/bigbluebutton-exporter/issues/3) for more details.

### HTTP Basic Auth
It is strongly recommended for your Nginx location directives (exporter & Netdata) to be behind HTTP Basic Auth.
This prevents unnecessary system information from being exposed to the public internet.

```bash
# First we will need apache2-utils
sudo apt-get install apache2-utils

# Create a username (e.g. monitoring) and password (prompted after you run the command)
sudo htpasswd -c /etc/nginx/.htpasswd monitoring  # user: monitoring
```

Afterwards add to each of your location directives the following two lines:
```
auth_basic "BigBlueButton";  # The contents of this can be anything
auth_basic_user_file /etc/nginx/.htpasswd;
```

Do not forget to reload Nginx (`sudo systemctl reload nginx`) and fix your Prometheus config to include the HTTP Basic Auth directive (for the exporter and Netdata), example bellow:
```
- job_name: 'bbb'
  scrape_interval: 5s
  scheme: https
  basic_auth:
    username: monitoring
    password: ukvK2Tn2dmmGZM7AxsGnXCZK
  static_configs:
  - targets: ['bbb.example.com', 'bbb2.example.com']
```

## Metrics
Gauges:
* bbb_meetings_participants - Total number of participants in all BigBlueButton meetings
* bbb_meetings_listeners - Total number of listeners in all BigBlueButton meetings
* bbb_meetings_voice_participants - Total number of voice participants in all BigBlueButton meetings
* bbb_meetings_video_participants - Total number of video participants in all BigBlueButton meetings
* bbb_meetings_participant_clients - Total number of participants in all BigBlueButton meetings by client
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
Add these to the `docker-compose.yml` file, see [https://docs.docker.com/compose/compose-file/#environment](https://docs.docker.com/compose/compose-file/#environment)
for instructions how.

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
* PORT
    * Required: false
    * Default: 9688
    * Values: <1 - 65535>
    
## Extras
Located in `extras` dir:
* docker-compose YAML file for bigbluebutton-exporter
* Grafana dashboards
