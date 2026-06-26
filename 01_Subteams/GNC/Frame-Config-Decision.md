# Frame Config — Decision Record

**Decision:** The ROV uses **8 thrusters** in a **vectored 6-DoF** layout
(BlueROV2 "Heavy" style). In ArduSub this is **`FRAME_CONFIG = 2`
(`vectored_6dof`)**. *Final as of June 2026.*

## Why / evidence
| Source | Evidence |
|---|---|
| GNC-ICD-01, Fig. 4 (wiring) | T1–T8 → ESC 1–8 → PWM channels 1–8; 3 servos on channels 14–16 |
| BOM | 4 CW + 4 CCW T200 thrusters = 8 (torque-balanced pairs) |
| CAD | `Horizontal Mount` + `Vertical Mount` parts; `Thruster Configuration Assembly.SLDASM` |
| Hardware | Navigator flight controller + Pi 5 + BlueOS + ArduSub |

8 thrusters give true 6-DoF: 4 horizontal (surge / sway / yaw) + 4 vertical
(heave / **roll / pitch**). A 6-thruster frame (2 vertical) could not control
roll and pitch — that's why 8 is required.

## Resolved conflict
Earlier design docs disagreed on count:
- `F&P/.../Thrusters - Number...` leaned toward **4** thrusters (no pitch).
- `Research Notes/GNC/ROV Software & Hardware Architecture...` cited a **4**-thruster baseline.
- BOM + ICD wiring specify **8**.

**8 is final.** The blank "6 positions" in the spec-sheet *template* is just an
unfilled template, not the design.

## Still to verify in CAD (does not affect the sim)
`vectored_6dof` assumes the 4 horizontal thrusters are mounted **~45° in the
corners**. Confirm in `Thruster Configuration Assembly.SLDASM` (top-down):
- Horizontals **45°-vectored** → `vectored_6dof` is exact, no extra work.
- Horizontals **straight** → custom motor matrix needed (recompile ArduSub).

Validated in SITL — see [SITL-Simulation/](SITL-Simulation/).
