from pymavlink import mavutil
import time

print("Connecting to drone...")
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

print("-- Taking off to 10 meters")
connection.mav.command_long_send(
    connection.target_system, connection.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0, 10
)
time.sleep(10) # Wait for takeoff to finish

# --- NEW: The Rectangle Loop ---
# We define the 4 legs of the rectangle as (X_Offset, Y_Offset, Description)
rectangle_legs = [
    (20, 0, "North 20m"),
    (0, 10, "East 10m"),
    (-20, 0, "South 20m"),
    (0, -10, "West 10m")
]

print("-- Starting rectangle pattern...")
for x_offset, y_offset, direction in rectangle_legs:
    print(f"   Flying {direction}...")
    
    connection.mav.set_position_target_local_ned_send(
        0,       
        connection.target_system, connection.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED, 
        0b0000111111111000, 
        x_offset,       
        y_offset,       
        0,       # 0 Z-offset keeps it exactly at 10m altitude
        0, 0, 0, 
        0, 0, 0, 
        0, 0     
    )
    
    # Wait 10 seconds for the drone to fly this specific leg 
    # before the loop sends the command for the next leg
    time.sleep(10)
# -------------------------------

print("-- Mission complete. Returning to Launch (RTL)...")
connection.mav.command_long_send(
    connection.target_system, connection.target_component,
    mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
    0, 0, 0, 0, 0, 0, 0, 0
)