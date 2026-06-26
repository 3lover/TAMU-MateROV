# Sample SITL runs

Example telemetry from the same scripted maneuver (settle → dive → cruise → turn
→ forward → strafe → surface), captured with `scripts/log_telemetry.py` and
rendered with `scripts/plot_telemetry.py`.

| Run | Vehicle model | Notes |
|---|---|---|
| `bluerov2-baseline_*` | ArduPilot stock BlueROV2 (10.5 kg) | reached ~5.8 m on the dive |
| `oceanus-22kg_*` | Team Oceanus model (22 kg, see [../OCEANUS-VEHICLE-MODEL.md](../OCEANUS-VEHICLE-MODEL.md)) | ~4.8 m on the same command — heavier vehicle dives shallower |

Each run has a `_dashboard.png` (shareable figure) and a `_telemetry.csv` (raw log).
These are illustrative; the Oceanus model uses **design-target/estimated** mass and
dimensions (no measured values exist yet) — regenerate once the ROV is weighed.

To make your own: see the "Capturing & presenting results" section in the
[main README](../README.md).
