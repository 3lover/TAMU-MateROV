# Sample SITL runs

Example telemetry from the same scripted maneuver (settle → dive → cruise → turn
→ forward → strafe → surface), captured with `scripts/log_telemetry.py` and
rendered with `scripts/plot_telemetry.py`.

| Run | Vehicle model | Dive (same command) |
|---|---|---|
| `bluerov2-baseline_*` | ArduPilot stock BlueROV2 (10.5 kg, T200-class 51.5 N) | ~5.8 m |
| `oceanus-td12_*` | Team Oceanus model: 22 kg + **Diamond Dynamics TD1.2** thrusters (24.5 N) — see [../OCEANUS-VEHICLE-MODEL.md](../OCEANUS-VEHICLE-MODEL.md) | ~3.5 m |
| `current-drift_*` | Oceanus model holding depth while a **0.6 m/s current** is switched on — drifts ~14 m east (ConOps current-compensation test) | n/a |
| `current-compensation_*` | `station_keeping.py` PID vs a **0.4 m/s current**: drifts ~3.9 m during a no-control phase, then recovers to within ~0.2 m and holds | n/a |
| `variable-current_*` | `station_keeping.py` (tuned) vs a **random current** that changes every ~3–4 s (13 changes): holds **mean 0.12 m / max 0.31 m**. `_response.png` overlays the disturbance and the position error | n/a |

Same command, shallower dive: the Oceanus ROV is heavier **and** its TD1.2 thrusters
push less than half a T200, so it's a slower, gentler vehicle. Top speed in the
Oceanus run is ~0.7 m/s vs ~1.2 m/s on the baseline.

Each run has a `_dashboard.png` (shareable figure) and a `_telemetry.csv` (raw log).
The Oceanus model still uses **design-target/estimated** mass and dimensions
(only the thrusters are a confirmed real value) — regenerate once the ROV is weighed.

To make your own: see "Capturing & presenting results" in the [main README](../README.md).
