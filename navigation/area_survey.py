from pymavlink import mavutil
import time
import math
import sys

# ==========================================
# USER INPUT: Field and Drone Specs
# ==========================================
print("--- Agricultural Coverage Mission (Failsafe Enabled) ---")

corners = [
    (10, 10),   
    (10, -10),  
    (-10, -10), 
    (-10, 10)   
]

ALTITUDE = 10 
SWATH_WIDTH = 1.0  
DRONE_SPEED = 10.0  
# ==========================================

# 1. Calculate the bounding box and waypoints
x_coords = [point[0] for point in corners]
y_coords = [point[1] for point in corners]

x_min, x_max = min(x_coords), max(x_coords)
y_min, y_max = min(y_coords), max(y_coords)

waypoints = []
current_x = x_min
direction = 1 

print("Calculating optimal flight path...")
while current_x <= x_max:
    if direction == 1:
        waypoints.append((current_x, y_min))
        waypoints.append((current_x, y_max))
    else:
        waypoints.append((current_x, y_max))
        waypoints.append((current_x, y_min))
    
    current_x += SWATH_WIDTH
    direction *= -1

print(f"Generated {len(waypoints)} waypoints to cover the field.")

# ==========================================
# EMERGENCY RTL FUNCTION
# ==========================================
def trigger_emergency_rtl(conn):
    print("\n[!!!] EMERGENCY TRIGGERED: Forcing drone into RTL mode [!!!]")
    try:
        # Setting the actual flight mode to RTL is the safest override command
        mode_id = conn.mode_mapping()['RTL']
        conn.mav.set_mode_send(
            conn.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id
        )
        print("-- Drone is returning to launch.")
    except Exception as e:
        print(f"Failed to send RTL command: {e}")

# ==========================================
# FLIGHT EXECUTION (Protected)
# ==========================================
connection = None

try:
    print("\nConnecting to drone...")
    connection = mavutil.mavlink_connection('udpin:0.0.0.0:14551')
    connection.wait_heartbeat()
    print("Drone discovered and connected!")

    print("Waiting for GPS lock (3D fix)...")
    while True:
        msg = connection.recv_match(type='GPS_RAW_INT', blocking=True)
        if msg and msg.fix_type >= 3:
            break

    print("Switching to GUIDED mode...")
    mode_id = connection.mode_mapping()['GUIDED']
    connection.mav.set_mode_send(
        connection.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )
    time.sleep(1)

    print("-- Arming motors")
    connection.mav.command_long_send(
        connection.target_system, connection.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0
    )
    connection.motors_armed_wait()

    print(f"-- Taking off to {ALTITUDE} meters")
    connection.mav.command_long_send(
        connection.target_system, connection.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, ALTITUDE
    )
    time.sleep(10) 

    print("\n-- Beginning Field Coverage --")
    print("   (Press Ctrl+C at any time to trigger emergency RTL)")
    current_x, current_y = 0, 0 

    for point_num, (target_x, target_y) in enumerate(waypoints, 1):
        print(f"Sweeping to WP {point_num}: ({target_x}m N, {target_y}m E)...")
        
        connection.mav.set_position_target_local_ned_send(
            0,       
            connection.target_system, connection.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, 
            0b0000111111111000, 
            target_x,       
            target_y,       
            -ALTITUDE,   
            0, 0, 0, 
            0, 0, 0, 
            0, 0     
        )
        
        distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
        flight_time = (distance / DRONE_SPEED) + 1.0 
        
        time.sleep(flight_time)
        current_x, current_y = target_x, target_y

    print("\n-- Field completely covered. Standard Return to Launch (RTL)...")
    mode_id = connection.mode_mapping()['RTL']
    connection.mav.set_mode_send(
        connection.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )

# --- THE FAILSAFE TRIGGERS ---
except KeyboardInterrupt:
    # Catches the user pressing Ctrl+C
    print("\n\n[WARNING] Mission aborted by pilot (Keyboard Interrupt).")
    if connection:
        trigger_emergency_rtl(connection)

except Exception as e:
    # Catches any Python crashes, math errors, or connection drops
    print(f"\n\n[FATAL ERROR] Script crashed: {e}")
    if connection:
        trigger_emergency_rtl(connection)