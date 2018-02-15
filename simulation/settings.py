

"""
Map layout constants. Size of map in X and Y direction.
Definition of roads and intersections
"""
MAP_SIZE_X = 61
MAP_SIZE_Y = 40
ROADS_X = [19, 20]
ROADS_Y = [19, 20, 40, 41]
INTERSECTIONS = [
    ((19, 19), (19, 20), (20, 19), (20, 20)),
    ((19, 40), (19, 41), (20, 40), (20, 41))
]

PROBABILITIES = {'left': 0.2, 'right': 0.4}


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
