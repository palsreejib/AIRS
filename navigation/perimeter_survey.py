from pymavlink import mavutil
import time
import math

# ==========================================
# USER INPUT: Define the 4 corners of the land 
# (X is North, Y is East in meters from launch point)
# ==========================================
print("--- Land Surveyor Mission ---")
corners = [
    (40, 30),   # Corner 1 (e.g., 20m North, 20m East)
    (20, 10),  # Corner 2
    (20, 20), # Corner 3
    (50, 40)   # Corner 4
]
# Add the first corner again to close the perimeter loop
corners.append(corners[0])

# Mission altitude in meters
ALTITUDE = 10 
# ==========================================

print("\nConnecting to drone...")
connection = mavutil.mavlink_connection('udpin:0.0.0.0:14551')
connection.wait_heartbeat()
print("Drone discovered and connected!")

print("Waiting for GPS lock (3D fix)...")
while True:
    msg = connection.recv_match(type='GPS_RAW_INT', blocking=True)
    if msg and msg.fix_type >= 3:
        print("-- GPS lock acquired!")
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
print("-- Armed!")

print(f"-- Taking off to {ALTITUDE} meters")
connection.mav.command_long_send(
    connection.target_system, connection.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0, ALTITUDE
)
time.sleep(10) # Wait for takeoff

# --- The Perimeter Logic ---
print("\n-- Beginning Perimeter Survey --")

# Keep track of where the drone currently is to calculate distance
current_x, current_y = 0, 0 

for point_num, (target_x, target_y) in enumerate(corners, 1):
    print(f"Flying to Point {point_num}: ({target_x}m North, {target_y}m East)...")
    
    # Send the target command using LOCAL_NED (Absolute position from home)
    connection.mav.set_position_target_local_ned_send(
        0,       
        connection.target_system, connection.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # <--- Changed to Absolute Grid
        0b0000111111111000, 
        target_x,       
        target_y,       
        -ALTITUDE,   # <--- Down is positive, so Up is negative!
        0, 0, 0, 
        0, 0, 0, 
        0, 0     
    )
    
    # Calculate straight-line distance to the next point (Pythagorean theorem)
    distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
    
    # Estimate flight time (assume drone flies ~5 m/s, plus a 3-second buffer to stabilize)
    flight_time = (distance / 5.0) + 3.0
    
    # Wait for the drone to reach the corner
    time.sleep(flight_time)
    
    # Update current position for the next calculation
    current_x, current_y = target_x, target_y

print("\n-- Perimeter complete. Returning to Launch (RTL)...")
connection.mav.command_long_send(
    connection.target_system, connection.target_component,
    mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
    0, 0, 0, 0, 0, 0, 0, 0
)