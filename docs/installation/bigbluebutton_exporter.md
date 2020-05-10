# Installation of BigBlueButton Exporter

## Docker Installation (Recommended)
These instructions will guide you through the installation procedure for BigBlueButton Exporter on your BigBlueButton server 
and direct the HTTP basic auth protected endpoint `/metrics/` to expose your BigBlueButtons server's metrics.
We assume you have a working installation of BigBlueButton with Nginx as the reverse proxy already set up.

!!! Info
    HTTP Basic Auth is required because each request to the `/metrics/` endpoint performs an API call to BigBlueButton which takes a couple of seconds. 
    
Prerequisite:

* Prometheus
* Docker
* docker-compose

### 1. Create directory
```shell
mkdir ~/bbb-exporter
```

### 2. Create docker-compose file
Copy [extras/docker-compose.exporter.yaml](https://github.com/greenstatic/bigbluebutton-exporter/tree/master/extras/docker-compose.exporter.yaml) 
to your BigBlueButton server into `~/bbb-exporter/docker-compose.yaml`

### 3. Create secrets file
Take a note of your BigBlueButton's API base url and secret by running:
```shell
bbb-conf --secret
```

Then create the file `~/bbb-exporter/secrets.env` and fill out the `API_BASE_URL` and `API_SECRET` variables with your details.
```text
API_BASE_URL=https://example.com/bigbluebutton/api/
API_SECRET=<secret>
```

!!! warning
    The API base url ends with `/api/` (beware of the trailing slash!). `bbb-conf --secret` will return the base url but
    not the base API url which has a `/api/` appended.

### 4. Start the container
```shell
sudo docker-compose up -d
```

The exporter should be running now.
However you will not be able to access it externally because the docker-compose file binded the exporters port only to localhost.
This is because we will use Nginx to act as a TLS termination proxy (reverse proxy with HTTPS support)  

### 5. Create HTTP basic auth password

!!! info
    For this you will need the handy `apache2-utils` package to create a password that will be used with HTTP basic auth by Nginx.
    You can install it (on Ubuntu) by running: `sudo apt-get install apache2-utils`.

Create a username (e.g. metrics) and password.
You will be prompted after you run the `htpasswd` command for the desired password.
```shell
# You may replace metrics with any desired username
sudo htpasswd -c /etc/nginx/.htpasswd metrics
```

!!! Warning
    If you already have `/etc/nginx/.htpasswd` file then do not add the `-c` flag, otherwise you will overwrite the file.

### 6. Add Nginx site configuration
Add the location directive to your Nginx web server (`/etc/nginx/sites-available/bigbluebutton`) that will proxy traffic to
`127.0.0.1:9688`.

```text
# BigBlueButton Exporter (metrics)
location /metrics/ {
  auth_basic "BigBlueButton";  # The contents of this can be anything
  auth_basic_user_file /etc/nginx/.htpasswd;
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

!!! Tip
    When upgrading BigBlueButton, the upgrade procedure will overwrite the contents of `/etc/nginx/sites-available/bigbluebutton`
    thereby causing you to lose access to your metrics. 
    So after the upgrade od BigBlueButton you will need to add the location directive again.
    
    You could also add a seperate site configuration, but this will require you do point another domain to the server to
    do virtual hosting and acquire a seperate HTTPS certificate.

### 7. Reload Nginx and test
First check if your Nginx configuration is syntactically valid:
```shell
sudo nginx -t
```

If everything is okay reload Nginx:
```shell
sudo systemctl reload nginx
```

Now you can try accessing the metrics on `/metrics` and typing in your username/password that you choose in 
[5. Create HTTP basic auth password](#5-create-http-basic-auth-password)

You should get the raw metrics in the Prometheus format.

### 8. Add the exporter to your Prometheus configuration
Now all that is left is to point your Prometheus to the exporter.

In your `prometheus.yaml` configuration add a new job specifying the target (url of the exporter) and HTTP basic auth
credentials.
Replace `example.com` with your BigBlueButton's domain.
```text
- job_name: 'bbb'
  scrape_interval: 5s
  scheme: https
  basic_auth:
    username: "<HTTP BASIC AUTH USERNAME>"
    password: "<HTTP BASIC AUTH PASSWORD>"
  static_configs:
  - targets: ['example.com']
```

!!! Tip
    You can scrape multiple exporters using a single job rule if they all have the same HTTP basic auth username/password.

### Updates
To update your BigBlueButton exporter all you have to do is change the docker image tag to the latest release 
(see [releases](https://github.com/greenstatic/bigbluebutton-exporter/releases) or [Docker image tags](https://hub.docker.com/r/greenstatic/bigbluebutton-exporter/tags)) 
in `~/bbb-exporter/docker-compose.yaml` and re-create the docker container by running:

```shell
cd ~/bbb-exporter
docker-compose up -d
```

Since the container doesn't store anything it is safe to destroy the container.

We recommend you "watch" on GitHub the [projects repository](https://github.com/greenstatic/bigbluebutton-exporter/) to be notified
on new releases.
This way you will be always notified when a new update for BigBlueButton Exporter is available.

## Systemd Installation (Not recommended)
This is an alternative installation guide that does not require docker and installs the exporter as a Systemd unit.

After the guide you will have:

* BigBlueButton Exporter installed system wide and you will be able to use systemctl to
start/stop/restart the exporter
* Nginx as a TLS termination proxy for the exporter

Installation should be on the BigBlueButton server, although it is possible to install it on a secondary machine, but 
this will require you to install Nginx and set it up by yourself.

### 1. Install Python 3 pip
```shell
sudo apt install python3-pip
```

### 2. Download the source code
```shell
cd /opt
sudo git clone https://github.com/greenstatic/bigbluebutton-exporter.git
cd bigbluebutton-exporter/
# It is recommended to checkout a release tag instead of using the master branch.
# We recommend selecting the latest release tag from:
# https://github.com/greenstatic/bigbluebutton-exporter/releases
sudo git checkout <RELEASE TAG>
# e.g. sudo git checkout v0.2.0
```

### 3. Create a non-privileged user for the exporter
```shell
sudo useradd -r -d /opt/bigbluebutton-exporter -s /usr/sbin/nologin bbb-exporter
sudo chown -R bbb-exporter:bbb-exporter /opt/bigbluebutton-exporter
```

### 4. Copy Systemd unit service and example settings
```shell
sudo cp /opt/bigbluebutton-exporter/extras/systemd/bigbluebutton-exporter.service /lib/systemd/system/
sudo cp -r /opt/bigbluebutton-exporter/extras/systemd/bigbluebutton-exporter /etc
```

### 5. Edit settings and replace `API_BASE_URL` and `API_SECRET`
```shell
sudo nano /etc/bigbluebutton-exporter/settings.env 
# or using Vim
sudo vim /etc/bigbluebutton-exporter/settings.env 
```

### 6. Start the bigbluebutton-exporter service
```shell
sudo systemctl start bigbluebutton-exporter
# optional - enable exporter to autostart when booting host
sudo systemctl enable bigbluebutton-exporter
```

### 7. Setup Nginx as a TLS termination proxy
Follow [steps 5 - 7](#5-create-http-basic-auth-password) from the Docker installation instructions.

### 8. Configure Prometheus
Follow [step 8](#8-add-the-exporter-to-your-prometheus-configuration) from the Docker installation instructions.

## Notes
### Multiple BigBlueButton Servers
You will need to install BigBlueButton Exporter on each server and then just add the server's domain to your
Prometheus `bbb` job target list.
