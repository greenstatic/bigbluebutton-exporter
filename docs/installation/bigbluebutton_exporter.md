# Installation of BigBlueButton Exporter

Two installation methods are supported:

* Docker (recommended)
* Systemd (not recommended)

We recommend Docker because it is easier to update, reproduce builds and comes with all dependencies pre-installed.

## Docker Installation (Recommended)
These instructions will guide you through the installation procedure for BigBlueButton Exporter on your BigBlueButton server 
and direct the HTTP basic auth protected endpoint `/metrics/` to expose your BigBlueButtons server's metrics.
We assume you have a working installation of BigBlueButton with Nginx as the reverse proxy already set up.

!!! Info
    HTTP Basic Auth is required because each request to the `/metrics/` endpoint performs an API call to BigBlueButton 
    which takes a couple of seconds. 
    
Prerequisite:

* Prometheus
* Docker
* docker-compose
* Working BigBlueButton server

### 1. Create directory
```shell
mkdir ~/bbb-exporter
```

### 2. Create docker-compose file
Copy [extras/docker-compose.exporter.yaml](https://github.com/greenstatic/bigbluebutton-exporter/tree/master/extras/docker-compose.exporter.yaml) 
to your BigBlueButton server into `~/bbb-exporter/docker-compose.yaml`.
Make sure to replace the Docker image tag to the [latest release](https://github.com/greenstatic/bigbluebutton-exporter/releases).

!!! Note
    We assume you will be running the exporter on the BigBlueButton server where you have access to the recordings
    directory (`/var/bigbluebutton`).
    We need access to this directory so we can efficiently compute the metrics for recordings.
    
    You can still run the exporter on a different host by disabling the optimization but will lose certain metrics 
    and increase scrape times. 
    
    See [details regarding the optimization](/exporter-user-guide/#optimizations). 

!!! tip
    Docker best practice: pin your docker image to a specific tag to have a reproducible environment.
    This also makes it easier to check which version you are running and which is the latest release.

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
    auth_basic "BigBlueButton Exporter";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:9688/;
    include proxy_params;

}
```

!!! Tip
    When upgrading BigBlueButton (using the script), the upgrade procedure will overwrite the contents of `/etc/nginx/sites-available/bigbluebutton`
    thereby causing you to lose access to your metrics. 
    So after the upgrade you will need to add the location directive again.
    
    You could also add a separate site configuration, but this will require you to point another domain to the server,
    configure virtual hosting and acquire a separate HTTPS certificate.

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
    You can scrape multiple exporters using a single job rule if they all have the same HTTP basic auth username/password in the Nginx termination proxy.
    See [Multiple BigBlueButton Servers](#multiple-bigbluebutton-servers) for details.

### Updates
To update your BigBlueButton exporter all you have to do is change the docker image tag to the latest release 
(see [releases](https://github.com/greenstatic/bigbluebutton-exporter/releases) or 
[Docker image tags](https://hub.docker.com/r/greenstatic/bigbluebutton-exporter/tags)) 
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

### 2. Download the source code and install dependencies
```shell
cd /opt
sudo git clone https://github.com/greenstatic/bigbluebutton-exporter.git
cd bigbluebutton-exporter/
# It is recommended to checkout a release tag instead of using the master branch.
# We recommend selecting the latest release tag from:
# https://github.com/greenstatic/bigbluebutton-exporter/releases
sudo git checkout <RELEASE TAG>
sudo pip3 install -r requirements.txt  # will install the Python dependencies system-wide
```

### 3. Create a non-privileged user for the exporter
```shell
sudo useradd -r -d /opt/bigbluebutton-exporter -s /usr/sbin/nologin bbb-exporter
sudo chown -R bbb-exporter:bbb-exporter /opt/bigbluebutton-exporter
```

### 4. Copy Systemd unit service and example settings
```shell
sudo cp /opt/bigbluebutton-exporter/extras/systemd/bigbluebutton-exporter.service /lib/systemd/system/
sudo mkdir /etc/bigbluebutton-exporter
sudo cp /opt/bigbluebutton-exporter/extras/systemd/bigbluebutton-exporter/* /etc/bigbluebutton-exporter
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

### Updates
To update the exporter all you need to do is issue a:
```shell
cd /opt/bigbluebutton-exporter
sudo git pull
sudo git checkout <RELEASE TAG>
sudo chown -R bbb-exporter:bbb-exporter /opt/bigbluebutton-exporter
sudo systemctl restart bigbluebutton-exporter
```

Check the [repository releases](https://github.com/greenstatic/bigbluebutton-exporter/releases) to get the latest tag.
It is recommended to watch the repository to be alerted when there is a new release available.

## Notes
### Multiple BigBlueButton Servers
There are two ways of configuring Prometheus to scrape multiple BigBlueButton exporters, the primary difference between the
two is that one supports having different HTTP Basic Auth usernames/passwords for each exporter and the other doesn't.

#### 1. Extending Prometheus targets (Recommended)
Pro:

* Simple configuration
* Dashboards work out of the box


Cons:

* All BigBlueButton exporters must have the same HTTP Basic Auth username/password

##### Configuration steps
1. Configure a single BigBlueButton exporter Prometheus scrape job
2. Configure the same HTTP Basic Auth username/password on all your Nginx TLS termination proxies 
(that act as a reverse proxy for your BigBlueButton exporter)
3. Append all the hosts to the Prometheus' `targets` field

Example scrape job, place this under `scrape_configs` in your Prometheus configuration:
```yaml
- job_name: 'bbb_node_exporter'
    metrics_path: '/node_exporter/metrics'
    params:
      format: [prometheus]
    honor_labels: true
    scheme: https
    basic_auth:
      username: <HTTP BASIC AUTH USERNAME>  # TODO - change
      password: <HTTP BASIC AUTH PASSWORD>  # TODO - change
    static_configs:
    # TODO - change, add all of your BigBlueButton exporter hosts
    - targets: ['bbb.example.com', 'bbb2.example.com', 'bbb3.example.com']
```


#### 2. Separate job (Not recommended)
Pro:

* All BigBlueButton exporters can have different HTTP Basic Auth usernames/passwords


Cons:

* More to configure

!!! Warning 
    This has not been tested and some changes to the provided Grafana dashboards might be required (in the future)!

##### Configuration steps
1. For each BigBlueButton exporter create a separate Prometheus scrape job 
2. Check to see if your Grafana dashboards are displaying all metrics correctly

Here is an example of two job scrape configuration (for two different exporters). 
Place this under `scrape_configs` in your Prometheus configuration for each job (exporter):

```yaml
# TODO - change job_name, this has to be different for each job
- job_name: 'bbb_node_exporter_1'
  metrics_path: '/node_exporter/metrics'
  params:
    format: [prometheus]
  honor_labels: true
  scheme: https
  basic_auth:
    username: <HTTP BASIC AUTH USERNAME>  # TODO - change
    password: <HTTP BASIC AUTH PASSWORD>  # TODO - change
  static_configs:
    - targets: ['bbb.example.com']  # TODO - change

# TODO - change job_name, this has to be different for each job
- job_name: 'bbb_node_exporter_2'
  metrics_path: '/node_exporter/metrics'
  params:
    format: [prometheus]
  honor_labels: true
  scheme: https
  basic_auth:
    username: <HTTP BASIC AUTH USERNAME>  # TODO - change
    password: <HTTP BASIC AUTH PASSWORD>  # TODO - change
  static_configs:
    - targets: ['bbb2.example.com']  # TODO - change
```
