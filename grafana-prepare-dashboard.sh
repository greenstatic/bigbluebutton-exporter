#!/usr/bin/env bash
set -e

# Removes the current object in templating Grafana dashboard field since this field includes
# the domain name of the instance variable of the exported dashboard.
# We do not wish to expose this since we do not want our BigBlueButton server to become public.

# Usage: ./grafana-prepare-dashboard.sh [input Grafana JSON dashboard] [output]

if [[ "$#" -ne 2 ]]; then
  echo "Bad arguments."
  echo "Usage: $0 [input Grafana JSON dashboard] [output]"
  exit 1
fi

set -x

jq 'del(.templating.list[].current)' "$1" > "$2"
set +x

echo "Done."
