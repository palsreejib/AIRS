import asyncio
from mavsdk import System

async def run():
    drone = System()
    
    print("Connecting to drone...")
    # 14550 is the default UDP port ArduPilot SITL broadcasts to
    await drone.connect(system_address="udpin://127.0.0.1:14551")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered and connected!")
            break

    print("Waiting for GPS lock...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- GPS lock acquired. Ready for flight.")
            break

    print("-- Arming motors")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    await asyncio.sleep(10)

    print("-- Landing")
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())
