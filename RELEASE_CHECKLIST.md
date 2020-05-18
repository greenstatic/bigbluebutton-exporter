1. Check the release version is correct in `bbb-exporter/settings.py`
2. `master` branch should contain the latest release
3. Create a release tag
4. Docker container should be built automatically, check on [Docker Hub](https://hub.docker.com/r/greenstatic/bigbluebutton-exporter/tags)
5. Update the container image version tag in `extras/docker-compose.exporter.yaml` and `extras/all_in_one_monitoring/docker-compose.yaml`
