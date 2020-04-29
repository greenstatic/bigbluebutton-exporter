# All-In-One Monitoring Stack
If you do not have any monitoring infrastructure setup you can following these instructions to setup the entire 
monitoring stack on your BigBlueButton server.

Monitoring Stack:

* BigBlueButton exporter
* Prometheus
* Grafana

Grafana will be exposed through the system installed Nginx which will act as a TLS termination proxy.

---
Prerequisites:

* Docker (you probably have this on your BigBlueButton server)
* docker-compose
* Nginx (that has TLS configured)

### Step-by-step Guide
### 1. Create directory
```shell
mkdir ~/bbb-monitoring
```

### 2. Copy configuration files
Copy all the files in [extras/all_in_one_monitoring](https://github.com/greenstatic/bigbluebutton-exporter/tree/master/extras/all_in_one_monitoring) 
to your server into `~/bbb-monitoring`

### 3. Add your secrets 
Get your BBB secret by running:
```shell
bbb-conf --secret
```

Then fill out `API_BASE_URL` and `API_SECRET` in `~/bbb-monitoring/secrets.env` with your details.

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

!!! Tip
    When upgrading BigBlueButton, the upgrade procedure will overwrite the contents of `/etc/nginx/sites-available/bigbluebutton`
    thereby causing you to lose access to your metrics. 
    So after the upgrade od BigBlueButton you will need to add the location directive again.
    
    You could also add a seperate site configuration, but this will require you do point another domain to the server to
    do virtual hosting and acquire a seperate HTTPS certificate.

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
[extras/dashboards/server_instace_netdata.json](https://github.com/greenstatic/bigbluebutton-exporter/tree/master/extras/dashboards/server_instance_netdata.json) 
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