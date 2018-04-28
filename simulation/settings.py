

"""
Map layout constants. Size of map in X and Y direction.
Definition of roads and intersections
"""

"""
# Large map
MAP_SIZE_X = 61
MAP_SIZE_Y = 40
ROADS_X = [19, 20]
ROADS_Y = [19, 20, 40, 41]
INTERSECTIONS = [
    ((19, 19), (19, 20), (20, 19), (20, 20)),
    ((19, 40), (19, 41), (20, 40), (20, 41))
]
"""

# Small map
MAP_SIZE_X = 12
MAP_SIZE_Y = 12

ROADS_X = [5, 6]
ROADS_Y = [5, 6]

INTERSECTIONS = [
    ((5, 5), (5, 6), (6, 5), (6, 6))
]



PROBABILITIES = {'left': 0.35, 'right': 0.30}

QUARTER_TURN_DEGREES = 90
HALF_TURN_DEGREES = 180
DRIVE_STEP = 0.25  # 20 centimeters per step

"""
NETWORK SETTINGS

For localhost testing use IP 127.0.0.1 and port 5005. 
You can then catch the message by running nc -ul 127.0.0.1 5005 in terminal

https://www.sans.org/security-resources/sec560/netcat_cheat_sheet_v1.pdf
"""

# Network settings
# We are using the broadcast option for UDP so this address needs to be a "certified" broadcast address
BROADCAST_IP = "127.255.255.255"
BROADCAST_PORT = 5005
BROADCAST_STEP = 1  # Send beacons every 1 second
# Multicast
MULTICAST_GROUP_IP = "224.3.29.71"
MULTICAST_PORT = 10000


# Lane detection settings
CAMERA_FRAME_RATE = 3
CAMERA_RESOLUTION = (752, 480)
CAMERA_VFLIP = False
CAMERA_HFLIP = False
CAMERA_WARMUP_TIME = 0.1

ACTUAL_CENTER = 383  # in pixels
LANE_DEBUG = False


# Traffic light
TRAFFIC_LIGHT_INTERVAL = 12  # Seconds
TRAFFIC_LIGHT_YELLOW_DURATION = 3  # Seconds
CAR_IS_PRIMARY = True
TRAFFIC_LIGHT_BROADCAST_PORT = 5555
