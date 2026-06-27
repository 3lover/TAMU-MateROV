# GNC SITL Simulation — ArduSub 6-DoF

Software-In-The-Loop (SITL) environment for validating Team Oceanus' control
systems and **custom 6-DoF frame configuration** before they touch hardware.

This runs the **real ArduSub firmware** against a simulated vehicle, so the same
frame mixing, PID loops, depth/heading hold, and MAVLink commands you test here
behave identically on the **Navigator + Raspberry Pi 5 + BlueOS** stack
(per `GNC-ICD-01`). That's why SITL is the right tool — not a hand-rolled
physics sim, which wouldn't match the autopilot.

> Covers **Goal 1 (Configure & Simulate 6-DoF Vehicle)** and **Practice Project 2
> (MAVLink heartbeat + IMU read)**, and gives the servo/thruster work
> (**Goal 2**) a place to run before hardware is ready.

---

## Status: validated end-to-end ✅

Built and run on macOS (Apple Silicon) with **ArduSub V4.5.7**. The sim boots
into `Frame: VECTORED_6DOF`, telemetry streams, and all six degrees of freedom
exercise the expected thrusters:

| Command | horizontal 1-4 | vertical 5-8 |
|---|---|---|
| neutral | 1500 1500 1500 1500 | 1500 1500 1500 1500 |
| forward | 1250 1250 1750 1750 | 1500 1500 1500 1500 |
| lateral | 1750 1250 1750 1250 | 1500 1500 1500 1500 |
| heave   | 1500 1500 1500 1500 | 1250 1250 1250 1250 |
| yaw     | 1750 1250 1250 1750 | 1500 1500 1500 1500 |
| roll    | 1500 1500 1500 1500 | 1750 1250 1750 1250 |
| pitch   | 1500 1500 1500 1500 | 1250 1250 1750 1750 |

Independent **roll and pitch** (driven by the 4 vertical thrusters) confirm true
6-DoF — a 2-vertical-thruster frame could not do this.

---

## The 6-DoF decision (why `vectored_6dof`)

| Frame | Thrusters | Controllable DoF | ArduSub `FRAME_CONFIG` |
|---|---|---|---|
| `vectored` (BlueROV2) | 6 (4 vec + 2 vert) | 4 — surge, sway, heave, yaw | 1 |
| **`vectored_6dof` (BlueROV2 Heavy)** | **8 (4 vec + 4 vert)** | **6 — adds roll & pitch** | **2** |

True, independently-controllable 6-DoF needs the **4 vertical thrusters** — with
only 2 vertical thrusters you cannot actively control roll and pitch. The
**8-thruster `vectored_6dof`** frame is the team's **final design** (confirmed
June 2026; BOM = 4 CW + 4 CCW T200s, ICD wiring T1–T8). See
[../Frame-Config-Decision.md](../Frame-Config-Decision.md).

---

## Prerequisites

- **Docker Desktop** (macOS/Windows/Linux). This is the clean path on macOS,
  where native ArduPilot builds are painful.
- **QGroundControl** (for visual flight + PID tuning) — optional but recommended.
- **Python 3.10+** on your host for the scripts (`pip install -r scripts/requirements.txt`).

## Quick start

```bash
cd "01_Subteams/GNC/SITL-Simulation"
./run_sitl.sh            # first run builds the image (~20-40 min, ~6 GB), then launches
```

When it prints the MAVProxy banner, the sim is live:

| Connect | Endpoint | For |
|---|---|---|
| GNC scripts / pymavlink | `tcp:127.0.0.1:5780` | telemetry + commands |
| QGroundControl | `tcp:localhost:5781` | add **Application Settings → Comm Links → Add → TCP**, host `localhost`, port `5781` |

Then, in another terminal:

```bash
cd "01_Subteams/GNC/SITL-Simulation"
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt

python3 scripts/sitl_check.py        # Project 2: heartbeat + live IMU / attitude / depth
python3 scripts/thruster_mixing.py   # drive each DoF, confirm 8-thruster frame mixing
```

Stop the sim with `Ctrl-C` in the `run_sitl.sh` terminal.

## Capturing & presenting results

No 3D viewer needed — record a run and turn it into one shareable figure:

```bash
# 1. start logging in one terminal (depth, attitude, position, power, thrusters)
python3 scripts/log_telemetry.py tcp:127.0.0.1:5780 run1.csv 10
# 2. fly the ROV (QGC joysticks, or thruster_mixing.py) — Ctrl-C the logger when done
# 3. render a dashboard PNG for the test report / presentation
python3 scripts/plot_telemetry.py run1.csv run1.png "Dive + Forward Test"
```

The dashboard shows the path travelled, depth profile, attitude, which thrusters
fired when, power draw, and speed — so testing reads as a picture, not numbers.

## Water-current testing (ConOps current compensation)

Stock ArduSub SITL is still water, so we patch the model (`apply_current_model.sh`,
baked into the image) so `SIM_WIND_SPD`/`SIM_WIND_DIR` act as a horizontal
**water current**. Set it live — no rebuild:

```bash
python3 scripts/inject_current.py 0.4 90   # 0.4 m/s toward east (090)
python3 scripts/inject_current.py 0        # back to still water
python3 scripts/inject_current.py demo     # drift at 0 / 0.5 / 1.0 m/s
```

Unpowered, the ROV drifts toward the current at the current speed — so you can
test drift detection and station-keeping / current-compensation control. See the
`current-drift_*` example in [sample-runs/](sample-runs/).

**Current compensation** — `station_keeping.py` is a PID position-hold (NED error
→ forward/lateral thrust, depth held by the autopilot) that cancels the drift:

```bash
python3 scripts/inject_current.py 0.4 90    # add a 0.4 m/s current
python3 scripts/station_keeping.py          # hold position against it
```

In testing it holds to ~**0.01 m** steady-state against a 0.4 m/s current (the
integral term removes the proportional droop). The `current-compensation_*`
sample shows a drift-then-recover run: ~3.9 m drift, recovered to within ~0.2 m.

---

## What's in here

| File | Purpose |
|---|---|
| `Dockerfile` | Builds ArduSub SITL from source (firmware = ground truth) |
| `sim_entry.sh` | Container entrypoint: starts SITL + a MAVProxy hub (multi-client) |
| `docker-compose.yml` / `run_sitl.sh` | One-command build & launch |
| `apply_oceanus_model.sh` + [`OCEANUS-VEHICLE-MODEL.md`](OCEANUS-VEHICLE-MODEL.md) | Patches SITL physics to our ROV's mass/size/thrust (edit + rebuild to update) |
| `params/vectored_6dof.parm` | The custom-frame parameter set (also `param load`-able onto the real Navigator) |
| `scripts/sitl_check.py` | Project 2 — heartbeat + IMU/attitude/depth stream |
| `scripts/thruster_mixing.py` | Drive each DoF via RC override, read SERVO_OUTPUT_RAW |
| `scripts/log_telemetry.py` | Record depth/attitude/position/battery/thrusters to CSV for reports |
| `scripts/plot_telemetry.py` | Turn a logged CSV into a shareable dashboard PNG (no 3D sim needed) |
| `scripts/inject_current.py` | Add a water current (ConOps drift / current-compensation testing) |
| `scripts/station_keeping.py` | PID position-hold that counters the current (ConOps current compensation) |
| `apply_current_model.sh` | Build-time patch making SIM_WIND act as a water current |

---

## Custom ArduSub frame config — step by step (deliverable)

1. **Pick the frame.** 8-thruster Heavy geometry → `FRAME_CONFIG = 2` (`vectored_6dof`).
   In SITL this is selected by `sim_vehicle.py -f vectored_6dof` (already wired in `sim_entry.sh`).
2. **On hardware**, set the same in QGroundControl → **Vehicle Setup → Frame**, or
   load `params/vectored_6dof.parm` via **Parameters → Tools → Load from file**.
3. **Confirm the mixing** with `scripts/thruster_mixing.py`: each DoF should move
   the expected group of thrusters (horizontals for surge/sway/yaw, verticals for
   heave/roll/pitch). Cross-check against `GNC-ICD-01 Figure 4 (Thruster
   Configuration)` and the
   [ArduSub thruster setup guide](https://www.ardusub.com/quick-start/vehicle-frame.html).
   (Note: ArduSub's `MAV_CMD_DO_MOTOR_TEST` is unreliable in SITL — it times out —
   so we exercise the mix via RC override instead.)
4. **Tune** depth-hold / heading-hold (`PSC_POSZ_P`, `ATC_ANG_YAW_P`) in QGC
   against SITL, then carry the values to the Navigator.
5. **Non-standard geometry?** If the thruster angles/positions differ from
   BlueROV2 Heavy, a fully custom motor matrix means editing
   `AP_Motors6DOF::setup_motors()` and rebuilding (bump `FRAME_CONFIG` to its
   Custom slot). Open an issue and we'll branch the Dockerfile for it.

---

## Troubleshooting

- **Build fails on `install-prereqs`** — usually a transient apt mirror issue;
  re-run `./run_sitl.sh`. The build layer is cached up to that point.
- **`FRAME_CONFIG` not 2 after boot** — connect with QGC or MAVProxy and
  `param set FRAME_CONFIG 2`, then reboot the sim. Report it so we can pin the param file.
- **Scripts can't connect** — make sure `run_sitl.sh` printed the MAVProxy banner
  and ports 5780/5781 aren't taken (`lsof -i :5780`).
- **Different ArduSub version** — rebuild with another release:
  `docker compose build --build-arg ARDUSUB_REF=Sub-4.1`.

## References

- ArduSub SITL setup — https://www.ardusub.com/developers/sitl.html
- ArduSub frames / thrusters — https://www.ardusub.com/quick-start/vehicle-frame.html
- pymavlink + ArduSub examples — https://www.ardusub.com/developers/pymavlink.html
- MAVProxy — https://ardupilot.org/mavproxy/
