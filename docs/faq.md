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
