import threading
from simulation.location.location import Location
from simulation.utils.direction import Direction
from simulation import settings
import logging
import random
import Queue


class Planner(threading.Thread):

    def __init__(self, threadId, name, position, to_dir, queue):
        """
        :type location: Location
        @type car: dict of simulation.car car
        """
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.name = name
        self.exitFlag = False
        self.route = []

        # Car variables
        self.position = position
        self.to_dir = to_dir

        self.plan = queue

        self.LOC = Location(self.position)

    def run(self):
        logging.debug("thread started")
        self.planner()
        logging.debug("thread stopped")

    def planner(self):
        while not self.exitFlag:
            if self.plan.qsize() < 6:
                self.calculate_next_step()

    def calculate_next_step(self):
        logging.debug("Calculating next step")
        if self.LOC.in_intersection(self.position):
            prob = random.uniform(0, 1)
            logging.debug("Car in intersection at " + str(self.position) + " probability " + str(prob))

            if self.to_dir == Direction.SOUTH:
                self._calculate_turn(prob, Direction.WEST, Direction.EAST, Direction.SOUTH)
            elif self.to_dir == Direction.NORTH:
                self._calculate_turn(prob, Direction.WEST, Direction.EAST, Direction.NORTH)
            elif self.to_dir == Direction.WEST:
                self._calculate_turn(prob, Direction.NORTH, Direction.SOUTH, Direction.WEST)
            else:
                self._calculate_turn(prob, Direction.NORTH, Direction.SOUTH, Direction.EAST)
        else:
            self.drive_straight(self.to_dir)

    def _calculate_turn(self, prob, left, right, straight):
        if prob <= settings.PROBABILITIES['left']:
            logging.debug("Turning left to " + left)
            self.quarter_turn(left)
        elif prob <= settings.PROBABILITIES['right']:
            logging.debug("Turning right to " + right)
            self.quarter_turn(right)
        else:
            logging.debug("Continuing on " + straight)
            self.drive_straight(straight)

    def quarter_turn(self, direction):
        new_pos = self.LOC.update_car_pos_turn(self.to_dir, direction)

        if new_pos == self.position:
            # TODO: Handle out of bounds
            logging.debug("quarter_turn: new pos is out-of-bounds, rejecting pos")
            return

        logging.debug("new pos accepted: " + str(new_pos))

        self.plan.put(
            {'command': 'quarter turn', 'next_pos': new_pos, 'to_dir': direction,
             'from_dir': self.to_dir})

        self.position = new_pos
        self.to_dir = direction
        return

    def drive_straight(self, direction):
        new_pos = self.LOC.update_car_pos(direction)

        if new_pos == self.position:
            # TODO: Handle out of bounds
            logging.debug("new pos is out-of-bounds, rejecting pos")
            self.handle_out_of_bounds()
            return

        logging.debug("drive straight, new pos " + str(new_pos))

        self.plan.put(
            {'command': 'straight', 'next_pos': new_pos, 'to_dir': direction,
             'from_dir': Direction().inverse_dir(direction)})
        self.position = new_pos
        self.to_dir = direction
        return

    def handle_out_of_bounds(self):
        # TODO: Assuming end of map
        # Set the inverse direction as new direction
        self.LOC.update_car_pos_turn(from_dir=self.to_dir, to_dir=Direction().inverse_dir(self.to_dir))

    def stop_thread(self):
        self.exitFlag = True

