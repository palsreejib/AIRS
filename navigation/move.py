from pymavlink import mavutil
import time

print("Connecting to drone...")
connection = mavutil.mavlink_connection('udpin:0.0.0.0:14551')
connection.wait_heartbeat()
print("Drone discovered and connected!")

# --- NEW: Wait for GPS Lock ---
print("Waiting for GPS lock (3D fix)...")
while True:
    # Listen specifically for the GPS telemetry packet
    msg = connection.recv_match(type='GPS_RAW_INT', blocking=True)
    
    # fix_type 3 means a solid 3D GPS lock
    if msg and msg.fix_type >= 3:
        print("-- GPS lock acquired!")
        break
# ------------------------------

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

# Wait 10 seconds for the drone to reach its altitude
time.sleep(10)

print("-- Moving 20 meters North and 20 meters East...")
connection.mav.set_position_target_local_ned_send(
    0,       
    connection.target_system, connection.target_component,
    mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED, 
    0b0000111111111000, 
    20,      # 20 meters North
    20,      # 20 meters East
    0,       # 0 meters Down (maintain altitude)
    0, 0, 0, 
    0, 0, 0, 
    0, 0     
)

# Give the drone 15 seconds to fly to the target
time.sleep(15)

print("-- Mission complete. Returning to Launch (RTL)...")
connection.mav.command_long_send(
    connection.target_system, connection.target_component,
    mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
    0, 0, 0, 0, 0, 0, 0, 0
)