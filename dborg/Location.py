import numpy
import Intersection
from Utils import Direction


class Location(object):
    """
    Map layout constants. Size of map in X and Y  direction.
    Which rows in X is roads and which columns in Y dir is rows.
    Which coordinates qualifies as a intersection
    """
    X_SIZE = 61
    Y_SIZE = 40
    ROADS_X_DIR = [19, 20]
    ROADS_Y_DIR = [19, 20, 40, 41]
    INTERSECTIONS = [
        ((19, 19), (19, 20), (20, 19), (20, 20)),
        ((19, 40), (19, 41), (20, 40), (20, 41))
    ]
    INITIAL_CAR_POS = (25, 20)

    map = numpy.array([[0 for j in range(X_SIZE)] for i in range(Y_SIZE)])
    intersections = []
    # map = [[0 for j in range(X_SIZE)] for i in range(Y_SIZE)]
    car = ()

    def __init__(self, initial_car_position=None):
        if initial_car_position:
            self.car = initial_car_position
        else:
            self.car = self.INITIAL_CAR_POS

        # Create intersections
        for intersect in self.INTERSECTIONS:
            self.intersections.append(Intersection.Intersection(intersect))

        self.initialize_map()

    def initialize_map(self):
        # Add roads
        for x_pos in self.ROADS_X_DIR:
            for y_pos in range(self.X_SIZE):
                self.map[x_pos][y_pos] = 1
        for y_pos in self.ROADS_Y_DIR:
            for x_pos in range(self.Y_SIZE):
                self.map[x_pos][y_pos] = 1
        # Add intersections to map
        for intersection in self.intersections:
            for point in intersection.get_pos():
                self.map[point] = str(intersection)
        return self.map

    def update_car_pos(self, direction):
        new_pos = ()
        if direction == Direction.NORTH:
            new_pos = (self.car[0] - 1, self.car[1])  # North: X-1, Y
        elif direction == Direction.SOUTH:
            new_pos = (self.car[0] + 1, self.car[1])  # South: X+1, Y
        elif direction == Direction.EAST:
            new_pos = (self.car[0], self.car[1] + 1)  # East: X+1, Y
        elif direction == Direction.WEST:
            new_pos = (self.car[0], self.car[1] - 1)  # West: X-1, Y

        if not self.check_out_of_bounds(new_pos):
            self.car = new_pos
            return True
        else:
            # TODO: Do some corrections
            print "Out of bounds!"
            return False

    def update_car_pos_turn(self, from_dir, to_dir):
        new_pos = ()
        if from_dir == Direction.NORTH:
            if to_dir == Direction.WEST:
                new_pos = (self.car[0], self.car[1] - 1)
            elif to_dir == Direction.EAST:
                new_pos = (self.car[0] + 1, self.car[1] + 1)
            elif to_dir == Direction.SOUTH:
                new_pos = (self.car[0], self.car[1] - 1)
        elif from_dir == Direction.SOUTH:
            if to_dir == Direction.WEST:
                new_pos = (self.car[0] - 1, self.car[1] - 1)
            elif to_dir == Direction.EAST:
                new_pos = (self.car[0], self.car[1] + 1)
            elif to_dir == Direction.NORTH:
                new_pos = (self.car[0], self.car[1] + 1)  # Here a turn is made
        elif from_dir == Direction.WEST:
            if to_dir == Direction.NORTH:
                new_pos = (self.car[0] - 1, self.car[1] + 1)
            elif to_dir == Direction.SOUTH:
                new_pos = (self.car[0] + 1, self.car[1])
            elif to_dir == Direction.EAST:
                new_pos = (self.car[0] + 1, self.car[1])
        elif from_dir == Direction.EAST:
            if to_dir == Direction.NORTH:
                new_pos = (self.car[0] - 1, self.car[1])
            elif to_dir == Direction.SOUTH:
                new_pos = (self.car[0] + 1, self.car[1] - 1)
            elif to_dir == Direction.WEST:
                new_pos = (self.car[0] - 1, self.car[1])

        if not self.check_out_of_bounds(new_pos):
            self.car = new_pos
            return True
        else:
            # TODO: Do some corrections
            print "Out of bounds!"
            return False

    def get_current_car_pos(self):
        return self.car

    def check_out_of_bounds(self, pos):
        """ Check if position is out of bounds (typically next position)"""
        if pos[0] < 0 or pos[0] > len(self.map) - 1 or pos[1] < 0 or pos[1] > len(self.map[0]) - 1:
            return True
        return self.map[pos] == 0

    def check_if_next_pos_is_intersection(self, pos):
        """ Check if next position is in intersection"""
        # Why not if pos in self.INTERSECTIONS?
        return self.map[pos] == 3

    def in_intersection(self, pos):
        """ Check if a position is in an intersection"""
        for intersection in self.INTERSECTIONS:
            if pos in intersection:
                return True
        return False
        # return pos in self.INTERSECTIONS

    def closest_intersection(self, distance=False):
        """
        Finds the closest intersection based on Euclidean Distance
        :param distance: Bool
        :return: distance or coordinates for closest intersection
        """
        closest_intersect_dist = 400
        closest_intersection = ()

        for intersection in self.INTERSECTIONS:
            for pos in intersection:
                dist = numpy.linalg.norm(numpy.array(self.car)-numpy.array(pos))
                if dist < closest_intersect_dist:
                    closest_intersect_dist = dist
                    closest_intersection = pos

        if distance:
            return closest_intersect_dist
        return closest_intersection

    def print_map(self):
        tmp_map = self.initialize_map()
        tmp_map[self.car] = 8

        # Print map with colors, makes it easier to see for debugging purpose
        for row in tmp_map:
            string = ''
            for pos in row:
                if pos == 0:
                    string += '\033[90m' + str(pos) + '\033[0m '
                elif pos == 8:
                    string += '\033[91m' + str(pos) + '\033[0m '
                elif pos == 1:
                    string += '\033[92m' + str(pos) + '\033[0m '
                else:
                    string += '\033[93m' + str(pos) + '\033[0m '
            print string
        print "\n"