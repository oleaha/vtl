from simulation.environment.map import Map
from simulation.utils.direction import Direction
import numpy

class Location:

    car = ()
    intersections = []
    map = ()

    def __init__(self, initial_car_position):
        self.car = initial_car_position
        self.map = Map()

    def update_car_pos(self, dir):
        next_pos = ()
        if dir == Direction.NORTH:
            new_pos = (self.car[0] - 1, self.car[1])  # North: X-1, Y
        elif dir == Direction.SOUTH:
            new_pos = (self.car[0] + 1, self.car[1])  # South: X+1, Y
        elif dir == Direction.EAST:
            new_pos = (self.car[0], self.car[1] + 1)  # East: X, Y+1
        elif dir == Direction.WEST:
            new_pos = (self.car[0], self.car[1] - 1)  # West: X, Y-1

        if self.check_out_of_bounds(new_pos):
            print "OOB: " + str(new_pos)
            return False

        self.car = new_pos
        return True

    def check_out_of_bounds(self, pos):
        pass

    def get_car_pos(self):
        return self.car

    def in_intersection(self, pos):
        """ Check if a given position is in an intersection """
        for intersection in self.intersections:
            if pos in intersection:
                return True
        return False

    def is_next_pos_in_intersection(self, pos):
        """ Check if a position is in an intersection """
        # TODO: Old version: return self.map[pos] == 3
        return pos in self.intersections

    def closest_intersection(self, distance=False):
        """ Find the closest intersection based on Euclidean Distance"""
        closest_dist = 400
        closest_intersection = ()

        for intersection in self.intersections:
            for pos in intersection:
                distance = numpy.linalg.norm(numpy.array(self.car) - numpy.array(pos))
                if distance < closest_dist:
                    closest_dist = distance
                    closest_intersection = pos

        if distance:
            return closest_dist
        return closest_intersection


lo = Location((12, 34))
