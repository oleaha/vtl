

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