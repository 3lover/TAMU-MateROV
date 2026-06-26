#!/usr/bin/env python3
"""GNC thruster-mixing check  —  actuate each of the 8 thrusters in turn.

Uses MAV_CMD_DO_MOTOR_TEST (same command as the team's existing motor-test
snippet) to spin each output of the vectored_6dof frame individually. Lets you
confirm the custom frame mapping in SITL, and later verify wiring/ESC order on
the real Navigator. No arming required.

Usage:
    python3 motor_test.py [conn] [throttle_pct] [seconds_each]
    python3 motor_test.py                       # tcp:127.0.0.1:5762, 10%, 2s
"""
import sys
import time
from pymavlink import mavutil

conn = sys.argv[1] if len(sys.argv) > 1 else "tcp:127.0.0.1:5762"
throttle = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
NUM_THRUSTERS = 8  # vectored_6dof: 4 vectored horizontal + 4 vertical

master = mavutil.mavlink_connection(conn)
master.wait_heartbeat()
print(f"Connected. Testing {NUM_THRUSTERS} thrusters @ {throttle:.0f}% for {seconds:.0f}s each.\n")

for motor in range(1, NUM_THRUSTERS + 1):
    print(f"  thruster {motor} ...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST, 0,
        motor,                                              # motor instance (1-based)
        mavutil.mavlink.MOTOR_TEST_THROTTLE_PERCENT,        # throttle type
        throttle,                                           # throttle value
        seconds,                                            # timeout (s)
        0, 0)                                               # motor count / test order
    time.sleep(seconds + 1)

print("\nDone — all thrusters cycled.")
