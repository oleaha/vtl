from simulation import settings
import numpy
from intersection import Intersection


class Map:

    map = []
    intersections = []

    def __init__(self):
        self.create_intersections()
        self.create_map()

    def create_intersections(self):
        for intersection in settings.INTERSECTIONS:
            self.intersections.append(Intersection(intersection))

    def create_map(self):
        self.map = numpy.array([[0 for j in range(settings.MAP_SIZE_X)] for i in range(settings.MAP_SIZE_Y)])

        # Add roads in X direction
        for xpos in settings.ROADS_X:
            for ypos in range(settings.MAP_SIZE_X):
                self.map[xpos][ypos] = 1
        # Add roads in Y direction
        for ypos in settings.ROADS_Y:
            for xpos in range(settings.MAP_SIZE_Y):
                self.map[xpos][ypos] = 1
        # Add intersections
        for intersection in self.intersections:
            for pos in intersection.get_pos():
                self.map[pos] = str(intersection)

        return self.map

    def get_map(self):
        return self.map

    def update_map_pos(self, pos, value):
        self.map[pos[1]][pos[2]] = value

    def __str__(self):
        pass