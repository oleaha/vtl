import threading
from simulation.location.location import Location
from simulation.car import Car
from simulation.utils.direction import Direction
from simulation import settings
import logging
import random


class Planner(threading.Thread):

    def __init__(self, threadId, name, location, car):
        """
        :type location: Location
        :type car: Car
        """
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.name = name
        self.exitFlag = False
        self.route = []
        self.location = location  # Passed from car.py
        self.car = car.car

    def run(self):
        logging.debug("thread started")
        self.planner()
        logging.debug("thread stopped")

    def planner(self):
        while not self.exitFlag:
            if len(self.route) < 6:
                self.calculate_next_step()

    def calculate_next_step(self):

        if self.location.in_intersection(self.location.get_car_pos()):
            prob = random.uniform(0, 1)
            if self.car['to_dir'] == Direction.SOUTH:
                self._calculate_turn(prob, Direction.WEST, Direction.EAST, Direction.SOUTH)
            elif self.car['to_dir'] == Direction.NORTH:
                self._calculate_turn(prob, Direction.WEST, Direction.EAST, Direction.NORTH)
            elif self.car['to_dir'] == Direction.WEST:
                self._calculate_turn(prob, Direction.NORTH, Direction.SOUTH, Direction.WEST)
            else:
                self._calculate_turn(prob, Direction.NORTH, Direction.SOUTH, Direction.EAST)
        else:
            self.drive_straight(self.car['to_dir'])

        self.route.append(self.location.get_car_pos())
        logging.debug(self.location.get_car_pos())

    def _calculate_turn(self, prob, left, right, straight):
        if prob <= settings.PROBABILITIES['left']:
            self.quarter_turn(left)
        elif prob <= settings.PROBABILITIES['right']:
            self.quarter_turn(right)
        else:
            self.drive_straight(straight)

    def quarter_turn(self, direction):
        pass

    def drive_straight(self, direction):
        pass

    def stop_thread(self):
        self.exitFlag = True

