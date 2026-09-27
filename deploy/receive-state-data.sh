#!/bin/bash
# Restricted upload for cloud agents. SSH forced-command only.
# Reads one JSON snapshot on stdin and loads it into us_pipelines.sqlite.
set -euo pipefail
cd /home/propeval/Energy_Infr
export ENERGY_WEB_ROOT=/var/www/energy
exec /usr/bin/python3 -m agents.load_incoming
