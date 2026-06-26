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

## ⚠️ Status: scaffold — build it and validate on your machine

These files were authored against ArduSub **Sub-4.5** but **have not yet been
built/run** on a GNC machine. Treat the first `./run_sitl.sh` as the validation
step. If the build or a frame default differs on your version, see
[Troubleshooting](#troubleshooting). Report what you hit so we can pin it down.

---

## The 6-DoF decision (why `vectored_6dof`)

| Frame | Thrusters | Controllable DoF | ArduSub `FRAME_CONFIG` |
|---|---|---|---|
| `vectored` (BlueROV2) | 6 (4 vec + 2 vert) | 4 — surge, sway, heave, yaw | 1 |
| **`vectored_6dof` (BlueROV2 Heavy)** | **8 (4 vec + 4 vert)** | **6 — adds roll & pitch** | **2** |

True, independently-controllable 6-DoF needs the **4 vertical thrusters** — with
only 2 vertical thrusters you cannot actively control roll and pitch. We're
targeting the **8-thruster `vectored_6dof`** frame. If the physical ROV ends up
with 6 thrusters, switch to `vectored` and update the objective to "4-DoF."

---

## Prerequisites

- **Docker Desktop** (macOS/Windows/Linux). This is the clean path on macOS,
  where native ArduPilot builds are painful.
- **QGroundControl** (for visual flight + PID tuning) — optional but recommended.
- **Python 3.10+** on your host for the scripts (`pip install -r scripts/requirements.txt`).

## Quick start

```bash
cd "25-26/01_Subteams/GNC/SITL-Simulation"
./run_sitl.sh            # first run builds the image (~20-40 min, ~3 GB), then launches
```

When it prints the MAVProxy banner, the sim is live:

| Connect | Endpoint | For |
|---|---|---|
| GNC scripts / pymavlink | `tcp:127.0.0.1:5762` | telemetry + commands |
| QGroundControl | `tcp:localhost:5763` | add **Application Settings → Comm Links → Add → TCP**, host `localhost`, port `5763` |

Then, in another terminal:

```bash
cd "25-26/01_Subteams/GNC/SITL-Simulation"
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt

python3 scripts/sitl_check.py      # Project 2: heartbeat + live IMU / attitude / depth
python3 scripts/motor_test.py      # cycle all 8 thrusters (verify frame mixing)
```

Stop the sim with `Ctrl-C` in the `run_sitl.sh` terminal.

---

## What's in here

| File | Purpose |
|---|---|
| `Dockerfile` | Builds ArduSub SITL from source (firmware = ground truth) |
| `sim_entry.sh` | Container entrypoint: starts SITL + a MAVProxy hub (multi-client) |
| `docker-compose.yml` / `run_sitl.sh` | One-command build & launch |
| `params/vectored_6dof.parm` | The custom-frame parameter set (also `param load`-able onto the real Navigator) |
| `scripts/sitl_check.py` | Project 2 — heartbeat + IMU/attitude/depth stream |
| `scripts/motor_test.py` | Actuate each of the 8 thrusters individually |

---

## Custom ArduSub frame config — step by step (deliverable)

1. **Pick the frame.** 8-thruster Heavy geometry → `FRAME_CONFIG = 2` (`vectored_6dof`).
   In SITL this is selected by `sim_vehicle.py -f vectored_6dof` (already wired in `sim_entry.sh`).
2. **On hardware**, set the same in QGroundControl → **Vehicle Setup → Frame**, or
   load `params/vectored_6dof.parm` via **Parameters → Tools → Load from file**.
3. **Confirm the mixing** with `scripts/motor_test.py`: each thruster 1–8 should
   spin in turn. Cross-check the spin direction/position against
   `GNC-ICD-01 Figure 4 (Thruster Configuration)` and the
   [ArduSub thruster setup guide](https://www.ardusub.com/quick-start/vehicle-frame.html).
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
  and ports 5762/5763 aren't taken (`lsof -i :5762`).
- **Different ArduSub version** — rebuild with another release:
  `docker compose build --build-arg ARDUSUB_REF=Sub-4.1`.

## References

- ArduSub SITL setup — https://www.ardusub.com/developers/sitl.html
- ArduSub frames / thrusters — https://www.ardusub.com/quick-start/vehicle-frame.html
- pymavlink + ArduSub examples — https://www.ardusub.com/developers/pymavlink.html
- MAVProxy — https://ardupilot.org/mavproxy/
