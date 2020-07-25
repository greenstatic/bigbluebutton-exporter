# All-In-One Monitoring Stack
If you do not have any monitoring infrastructure setup you can following these instructions to setup the entire 
monitoring stack on your BigBlueButton server.

Monitoring Stack:

* BigBlueButton exporter
* Prometheus (incl. node_exporter)
* Grafana

Grafana will be exposed through the system installed Nginx which will act as a TLS termination proxy.

---
Prerequisites:

* Docker (you probably have this on your BigBlueButton server)
* docker-compose (recent version with compose file format version 3.2 support)
* Nginx (that has TLS configured)

!!! Warning
    Follow [Docker's official installation instructions](https://docs.docker.com/engine/install/ubuntu/) instead of 
    installing docker-compose from Ubuntu's official repository since it is outdated and does not support compose file 
    format v3.2 (as of April 29, 2020).
    

### Step-by-step Guide
### 1. Create directory
```shell
mkdir ~/bbb-monitoring
```

### 2. Copy configuration files
Copy all the files in [extras/all_in_one_monitoring](https://github.com/greenstatic/bigbluebutton-exporter/tree/master/extras/all_in_one_monitoring) 
to your server into `~/bbb-monitoring`

And replace all the references to `example.com` with your BigBlueButton domain.

Make sure to replace the exporters Docker image tag to the [latest release](https://github.com/greenstatic/bigbluebutton-exporter/releases).

If you are not running on your BigBlueButton server, then you will need to disable the 
`RECORDINGS_METRICS_READ_FROM_DISK` optimization by removing it from the docker-compose file
and the `/var/bigbluebutton` volume bind mount.
This will have the unfortunate consequence of dramatically increasing scrape times when your BigBlueButton
server will have many recordings.
It is also smart to increase the `scrape_timeout` value when disabling the optimization, see 
[All in One Monitoring Stack BrokenPipeError](/faq/#all-in-one-monitoring-stack-brokenpipeerror) for details.

!!! tip
    Docker best practice: pin your docker image to a specific tag to have a reproducible environment.
    This also makes it easier to check which version you are running and which is the latest release.

!!! note
    You will configure `https://example.com/monitoring` in [step 5: Configure Nginx](#5-configure-nginx).

### 3. Add your secrets 
Get your BBB secret by running:
```shell
bbb-conf --secret
```

Then fill out `API_BASE_URL` and `API_SECRET` in `~/bbb-monitoring/bbb_exporter_secrets.env` with your details.

!!! warning
    The API base url ends with `/api/` (beware of the trailing slash!). `bbb-conf --secret` will return the base url but
    not the base API url which has a `/api/` appended.

### 4. Start the services
```shell
cd ~/bbb-monitoring
sudo docker-compose up -d
```

### 5. Configure Nginx
Add the location directive to your Nginx web server (`/etc/nginx/sites-available/bigbluebutton`) that will proxy traffic to
`127.0.0.1:3001`.

```text
# BigBlueButton monitoring
location /monitoring/ {
  proxy_pass         http://127.0.0.1:3001/;
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

!!! Note
    If you would like to change the URL you will need to update the docker-compose grafana `GF_SERVER_ROOT_URL` env 
    variable as well.

!!! Tip
    When upgrading BigBlueButton, the upgrade procedure will overwrite the contents of `/etc/nginx/sites-available/bigbluebutton`
    thereby causing you to lose access to your metrics. 
    So after the upgrade to BigBlueButton you will need to add the location directive again.
    
    You could also add a separate site configuration, but this will require you to point another domain to the server to
    do virtual hosting and acquire a separate HTTPS certificate.

### 6. Setup Grafana
Login to Grafana (https://example.com/monitoring) in your web browser (admin:admin) and **change the password**.

Add Prometheus as a data source (_Add data source -> Prometheus_) and entering the following configuration:
```text
URL: http://localhost:9090
```

!!! note
    The `prometheus` DNS entry will be resolved by Docker since Grafana is running within the same Docker network (our
    docker-compose configuration automates this).

Now it is time to finally import the fancy dashboards.
In the left menu click on _+ icon -> import_

In the JSON field copy/paste the contents of
[extras/dashboards/server_instance_node_exporter.json](https://github.com/greenstatic/bigbluebutton-exporter/tree/master/extras/dashboards/server_instance_node_exporter.json) 
Grafana dashboard.

You are done 👏👏!

!!! Warning
    You can edit your dashboard as much as you like, but note that you will lose your changes if you will re-import updated 
    versions of the dashboard. 
    So you will have to manually patch the dashboard when we update the dashboard json files in the repository.

## Updates
Follow [Installation of BigBlueButton Exporter -> Updates](./bigbluebutton_exporter.md#updates) but instead of 
`cd ~/bbb-exporter` you will have to `cd ~/bbb-monitoring`.

Check the releases for the rest of the services (Prometheus, Grafana & node_exporter) on their respected websites for 
details on the latest Docker image release tag.
