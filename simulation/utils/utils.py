from simulation.utils.direction import Direction
from simulation import settings


def calculate_quarter_spin_degree(from_dir, to_dir):
    if from_dir == Direction.WEST:
        if to_dir == Direction.NORTH:
            return settings.QUARTER_TURN_DEGREES
        return -settings.QUARTER_TURN_DEGREES
    elif from_dir == Direction.EAST:
        if to_dir == Direction.SOUTH:
            return settings.QUARTER_TURN_DEGREES
        return -settings.QUARTER_TURN_DEGREES
    elif from_dir == Direction.NORTH:
        if to_dir == Direction.WEST:
            return -settings.QUARTER_TURN_DEGREES
        return settings.QUARTER_TURN_DEGREES
    else:
        if to_dir == Direction.EAST:
            return -settings.QUARTER_TURN_DEGREES
        return settings.QUARTER_TURN_DEGREES
