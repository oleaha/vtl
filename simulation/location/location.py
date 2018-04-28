from simulation.environment.map import Map
from simulation.utils.direction import Direction
import numpy
import logging
from simulation import settings


class Location:

    car = ()
    map = ()

    def __init__(self, initial_car_position, use_traffic_light=False):
        self.car = initial_car_position
        self.map = Map(use_traffic_light)

    def update_car_pos(self, dir):
        next_pos = ()
        old_pos = self.car

        if dir == Direction.NORTH:
            next_pos = (self.car[0] - 1, self.car[1])  # North: X-1, Y
        elif dir == Direction.SOUTH:
            next_pos = (self.car[0] + 1, self.car[1])  # South: X+1, Y
        elif dir == Direction.EAST:
            next_pos = (self.car[0], self.car[1] + 1)  # East: X, Y+1
        elif dir == Direction.WEST:
            next_pos = (self.car[0], self.car[1] - 1)  # West: X, Y-1

        # If the new position is out of bounds, return its current position
        if self.check_out_of_bounds(next_pos):
            return old_pos

        self.car = next_pos
        return self.car

    def update_car_pos_turn(self, to_dir, new_to_dir):
        next_pos = ()

        #logging.debug("car is turning from (going)" + str(to_dir) + " to (new going)" + str(new_to_dir))

        if to_dir == Direction.NORTH:
            if new_to_dir == Direction.WEST:
                next_pos = (self.car[0] - 1, self.car[1] - 1)
            elif new_to_dir == Direction.EAST:
                next_pos = (self.car[0], self.car[1] + 1)
            elif new_to_dir == Direction.SOUTH:
                next_pos = (self.car[0], self.car[1] - 1)
        elif to_dir == Direction.SOUTH:
            if new_to_dir == Direction.WEST:
                next_pos = (self.car[0], self.car[1] - 1)
            elif new_to_dir == Direction.EAST:
                next_pos = (self.car[0] + 1, self.car[1] + 1)
            elif new_to_dir == Direction.NORTH:
                next_pos = (self.car[0], self.car[1] + 1)
                #logging.debug("temp new pos is " + str(next_pos))
        elif to_dir == Direction.WEST:
            if new_to_dir == Direction.NORTH:
                next_pos = (self.car[0] - 1, self.car[1])
            elif new_to_dir == Direction.SOUTH:
                next_pos = (self.car[0] + 1, self.car[1] - 1)
            elif new_to_dir == Direction.EAST:
                next_pos = (self.car[0] + 1, self.car[1])
        elif to_dir == Direction.EAST:
            if new_to_dir == Direction.NORTH:
                next_pos = (self.car[0] - 1, self.car[1] + 1)
            elif new_to_dir == Direction.SOUTH:
                next_pos = (self.car[0] + 1, self.car[1])
            elif new_to_dir == Direction.WEST:
                next_pos = (self.car[0] - 1, self.car[1])

        #logging.debug("update_car_pos_turn: next pos: " + str(next_pos))
        self.car = next_pos
        return self.car

    def check_out_of_bounds(self, pos):
        #logging.debug("Check if pos is OOB: " + str(pos))
        if pos[0] < 0 or pos[0] > settings.MAP_SIZE_Y - 1 or pos[1] < 0 or pos[1] > settings.MAP_SIZE_X - 1:
            #logging.debug("Pos is OOB")
            return True
        return self.map.get_map()[pos] == 0

    def get_car_pos(self):
        return self.car

    def get_intersection(self, pos):
        for intersection in self.map.get_intersections():
            if pos in intersection.get_pos():
                return intersection

    """ Check if a given position is in an intersection """
    def in_intersection(self, pos):
        return self.map.get_map()[pos] == 3

    """ Check if a position is in an intersection """
    def is_next_pos_in_intersection(self, pos):
        return self.map.get_map()[pos] == 3

    """ Find the closest intersection based on Euclidean Distance"""
    def closest_intersection(self, distance=False):

        closest_dist = 400
        closest_intersection = ()

        for intersection in self.map.get_intersections():
            for pos in intersection:
                distance = numpy.linalg.norm(numpy.array(self.car) - numpy.array(pos))
                if distance < closest_dist:
                    closest_dist = distance
                    closest_intersection = pos

        if distance:
            return closest_dist
        return closest_intersection
