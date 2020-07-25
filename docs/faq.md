# FAQ

## Scalelite Support
BigBlueButton Exporter can be used alongside Scalelite.
In fact the exporter doesn't need to know anything about Scalelite (or 
Scalelite about the exporter) since the exporter still needs to be configured
to scrape metrics from the BigBlueButton server's API.
See [comment in Issue #31](https://github.com/greenstatic/bigbluebutton-exporter/issues/31#issuecomment-632335583).


## My `CA_BUNDLE` for the `TLS_VERIFY` environment variable is not working
If you will specify the _directory flavor_, make sure the directory is filled with public keys of 
your trusted CA in PEM format.

If you will specify the _file flavor_ (e.g. `TLS_VERIFY=/app/CA_BUNDLE.txt`), make sure the file contains an appended 
list of all your trusted PEM formatted CA's. 
Non-working example to denote the format:

```
-----BEGIN CERTIFICATE-----
... // PEM formated CA
-----END CERTIFICATE-----

-----BEGIN CERTIFICATE-----
... // PEM formated CA
-----END CERTIFICATE-----

-----BEGIN CERTIFICATE-----
... // PEM formated CA
-----END CERTIFICATE-----
```

## All in One Monitoring Stack BrokenPipeError
If you get a `BrokenPipeError` exception similar to:
```
bbb-exporter | ----------------------------------------
bbb-exporter | 2020-07-09 01:38:25,635 [INFO]: Collecting metrics from BigBlueButton API
bbb-exporter | 2020-07-09 01:38:32,497 [INFO]: Finished collecting metrics from BigBlueButton API
bbb-exporter | ----------------------------------------
bbb-exporter | Exception happened during processing of request from ('127.0.0.1', 48190)
bbb-exporter | Traceback (most recent call last):
bbb-exporter | File "/usr/local/lib/python3.7/socketserver.py", line 650, in process_request_thread
bbb-exporter | self.finish_request(request, client_address)
bbb-exporter | File "/usr/local/lib/python3.7/socketserver.py", line 360, in finish_request
bbb-exporter | self.RequestHandlerClass(request, client_address, self)
bbb-exporter | File "/usr/local/lib/python3.7/socketserver.py", line 720, in init
bbb-exporter | self.handle()
bbb-exporter | File "/usr/local/lib/python3.7/http/server.py", line 426, in handle
bbb-exporter | self.handle_one_request()
bbb-exporter | File "/usr/local/lib/python3.7/http/server.py", line 414, in handle_one_request
bbb-exporter | method()
bbb-exporter | File "/usr/local/lib/python3.7/site-packages/prometheus_client/exposition.py", line 159, in do_GET
bbb-exporter | self.wfile.write(output)
bbb-exporter | File "/usr/local/lib/python3.7/socketserver.py", line 799, in write
bbb-exporter | self._sock.sendall(b)
bbb-exporter | BrokenPipeError: [Errno 32] Broken pipe
```

This is caused by Prometheus closing the metrics scrapping HTTP request to the exporter because the request duration 
exceeds the Prometheus defined `scrape_timeout` value.
The Prometheus config (`prometheus.yaml`) file bundled with the All in One Monitoring Stack has the default `scrape_timeout`
set to 15 seconds.
The recommended way of fixing this is to enable the [RECORDINGS_METRICS_READ_FROM_DISK](/exporter-user-guide/#optimizations) 
optimization which should dramatically reduce scraping times.

You could also [override the scrape_timeout value](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config) 
for the bbb_exporter job but this should be only done in cases where enabling the `RECORDINGS_METRICS_READ_FROM_DISK`
optimization is unfeasible.
