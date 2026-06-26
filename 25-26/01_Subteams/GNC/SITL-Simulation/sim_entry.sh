#!/usr/bin/env bash
# Container entrypoint: launch ArduSub SITL headless, then a MAVProxy hub that
# fans the MAVLink stream out to two listening TCP ports so multiple clients
# (QGroundControl + pymavlink scripts) can connect at once.
set -euo pipefail
cd /opt/ardupilot

echo ">> Starting ArduSub SITL (frame: vectored_6dof)…"
Tools/autotest/sim_vehicle.py -v ArduSub -f vectored_6dof \
    --no-rebuild --no-mavproxy -w -l 33.6,-118.0,0,0 \
    >/tmp/sitl.log 2>&1 &

echo ">> Waiting for firmware on tcp:5760…"
for _ in $(seq 1 90); do
    (echo > /dev/tcp/127.0.0.1/5760) 2>/dev/null && break
    sleep 1
done

echo ">> SITL up. Starting MAVProxy hub:"
echo "     tcp:localhost:5762  ->  GNC scripts / pymavlink"
echo "     tcp:localhost:5763  ->  QGroundControl (add a TCP comm link)"
exec mavproxy.py --master tcp:127.0.0.1:5760 \
    --out tcpin:0.0.0.0:5762 \
    --out tcpin:0.0.0.0:5763 \
    --non-interactive
