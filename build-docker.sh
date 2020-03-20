#!/usr/bin/env/bash
set -e

# Get current version
SCRIPT_PATH=$(dirname "$0")
DOCKERFILE_PATH=$SCRIPT_PATH
SETTINGS_PY=${SCRIPT_PATH}/bbb-exporter/settings.py

VERSION_MAJOR=$(cat $SETTINGS_PY | grep "MAJOR\ *=\ *" | rev | cut -d " " -f 1 | cut -d "=" -f 1 | rev)
VERSION_MINOR=$(cat $SETTINGS_PY | grep "MINOR\ *=\ *" | rev | cut -d " " -f 1 | cut -d "=" -f 1 | rev)
VERSION_BUGFIX=$(cat $SETTINGS_PY | grep "BUGFIX\ *=\ *" | rev | cut -d " " -f 1 | cut -d "=" -f 1 | rev)

VERSION="${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_BUGFIX}"

# Build docker image
cd ${DOCKERFILE_PATH}
docker build -t greenstatic/bigbluebutton-exporter:v${VERSION} -t greenstatic/bigbluebutton-exporter:latest .