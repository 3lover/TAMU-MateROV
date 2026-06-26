#!/usr/bin/env bash
# Build (first run only) and launch ArduSub SITL.
#   QGroundControl -> add TCP link to  localhost:5763
#   GNC scripts     ->  tcp:127.0.0.1:5762   (the scripts default to this)
# Stop with Ctrl-C.
set -euo pipefail
cd "$(dirname "$0")"
exec docker compose up --build
