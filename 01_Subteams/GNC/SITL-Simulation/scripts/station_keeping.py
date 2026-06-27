#!/usr/bin/env python3
"""GNC station-keeping — hold horizontal position against a water current.

A PID controller on NED position error, driving forward/lateral thrust in
DEPTH_HOLD mode (the autopilot holds depth; this loop holds the horizontal
position). Demonstrates the ConOps "current compensation / detect drift" task —
mirrors the pseudocode's position tracking + control. The integral term cancels
the steady-state droop a P/PD controller leaves against a constant current.

Run `inject_current.py <spd> <dir>` first to add a disturbance, then this.

Usage:
    python3 station_keeping.py [conn] [seconds] [kp] [kd] [ki]
    python3 station_keeping.py                      # tcp:127.0.0.1:5781, 30s
"""
import math
import sys
import time
from pymavlink import mavutil

conn = sys.argv[1] if len(sys.argv) > 1 else "tcp:127.0.0.1:5781"
duration = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
KP = float(sys.argv[3]) if len(sys.argv) > 3 else 440.0   # PWM per metre of error
KD = float(sys.argv[4]) if len(sys.argv) > 4 else 230.0   # PWM per (m/s) of closing speed
KI = float(sys.argv[5]) if len(sys.argv) > 5 else 210.0   # PWM per (m·s) accumulated error
LIMIT = 400                                               # max PWM offset from 1500
I_LIMIT = 300                                             # anti-windup clamp on the integral term
SUB_MODE_DEPTH_HOLD = 2

m = mavutil.mavlink_connection(conn)
m.wait_heartbeat()
for mid, hz in [(mavutil.mavlink.MAVLINK_MSG_ID_LOCAL_POSITION_NED, 10),
                (mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 10)]:
    m.mav.command_long_send(m.target_system, m.target_component,
                            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
                            mid, int(1e6 / hz), 0, 0, 0, 0, 0)

# wait for a valid position estimate
state = {"x": None, "y": None, "vx": 0.0, "vy": 0.0, "yaw": 0.0}
def pump(timeout=0.0):
    t0 = time.time()
    while True:
        msg = m.recv_match(type=["LOCAL_POSITION_NED", "ATTITUDE"], blocking=True, timeout=1)
        if msg:
            if msg.get_type() == "LOCAL_POSITION_NED":
                state.update(x=msg.x, y=msg.y, vx=msg.vx, vy=msg.vy)
            else:
                state["yaw"] = msg.yaw
        if timeout == 0.0 and state["x"] is not None:
            return
        if timeout and time.time() - t0 > timeout:
            return

print("waiting for position estimate...")
t = time.time()
while state["x"] is None and time.time() - t < 30:
    pump(timeout=0.2)
if state["x"] is None:
    print("no position estimate; aborting"); raise SystemExit(1)

m.mav.param_set_send(m.target_system, m.target_component, b"ARMING_CHECK", 0,
                     mavutil.mavlink.MAV_PARAM_TYPE_INT8)
time.sleep(0.4)
m.mav.set_mode_send(m.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                    SUB_MODE_DEPTH_HOLD)
m.mav.command_long_send(m.target_system, m.target_component,
                        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 21196, 0, 0, 0, 0, 0)
m.motors_armed_wait()

tx, ty = state["x"], state["y"]   # hold the position we started at
print(f"holding target N={tx:.2f} E={ty:.2f} for {duration:.0f}s (Kp={KP:.0f} Kd={KD:.0f} Ki={KI:.0f})\n")


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


t0 = time.time()
last_print = 0.0
max_err = 0.0
i_fwd = i_lat = 0.0
t_prev = time.time()
while time.time() - t0 < duration:
    pump(timeout=0.05)
    now = time.time()
    dt = now - t_prev
    t_prev = now
    yaw = state["yaw"]
    # position error in earth frame
    e_n, e_e = tx - state["x"], ty - state["y"]
    # rotate error + velocity into body frame (x=forward, y=right/lateral)
    c, s = math.cos(yaw), math.sin(yaw)
    fwd_err = e_n * c + e_e * s
    lat_err = -e_n * s + e_e * c
    fwd_vel = state["vx"] * c + state["vy"] * s
    lat_vel = -state["vx"] * s + state["vy"] * c
    # integral with anti-windup
    i_fwd = clamp(i_fwd + fwd_err * dt, -I_LIMIT / max(KI, 1e-6), I_LIMIT / max(KI, 1e-6))
    i_lat = clamp(i_lat + lat_err * dt, -I_LIMIT / max(KI, 1e-6), I_LIMIT / max(KI, 1e-6))
    # PID -> thrust commands
    cmd_fwd = clamp(KP * fwd_err - KD * fwd_vel + KI * i_fwd, -LIMIT, LIMIT)
    cmd_lat = clamp(KP * lat_err - KD * lat_vel + KI * i_lat, -LIMIT, LIMIT)
    ch = [1500] * 8
    ch[4] = int(1500 + cmd_fwd)   # forward
    ch[5] = int(1500 + cmd_lat)   # lateral
    m.mav.rc_channels_override_send(m.target_system, m.target_component, *ch)
    err = math.hypot(e_n, e_e)
    max_err = max(max_err, err)
    if time.time() - last_print > 2:
        print(f"  t={time.time()-t0:4.1f}s  error={err:4.2f} m  (dN={e_n:+.2f} dE={e_e:+.2f})")
        last_print = time.time()
    time.sleep(0.05)

# release + disarm
m.mav.rc_channels_override_send(m.target_system, m.target_component, *([1500] * 8))
m.mav.command_long_send(m.target_system, m.target_component,
                        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)
print(f"\nDone. Max position error held: {max_err:.2f} m")
