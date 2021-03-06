import threading
from simulation.location.location import Location
from simulation.utils.direction import Direction
from simulation import settings
import logging
import random


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
        self.prev_pos = position
        self.position = position
        self.to_dir = to_dir

        self.plan = queue

        self.LOC = Location(self.position)

    def run(self):
        logging.debug("Planner started")
        self.planner()
        logging.debug("Planner stopped")

    def planner(self):
        while not self.exitFlag:
            if self.plan.qsize() < 6:
                self.calculate_next_step()

    def calculate_next_step(self):
        # Only turn in intersection if the previous position was not in an intersection
        if self.LOC.in_intersection(self.position) and not self.LOC.in_intersection(self.prev_pos):
            prob = random.uniform(0, 1)

            if self.to_dir == Direction.SOUTH:
                self._calculate_turn(prob, Direction.EAST, Direction.WEST, Direction.SOUTH)
            elif self.to_dir == Direction.NORTH:
                self._calculate_turn(prob, Direction.WEST, Direction.EAST, Direction.NORTH)
            elif self.to_dir == Direction.WEST:
                self._calculate_turn(prob, Direction.SOUTH, Direction.NORTH, Direction.WEST)
            else:
                self._calculate_turn(prob, Direction.NORTH, Direction.SOUTH, Direction.EAST)
        else:
            self.drive_straight(self.to_dir)

    def _calculate_turn(self, prob, left, right, straight):
        if prob <= settings.PROBABILITIES['left']:
            self.quarter_turn(left)
        elif prob <= settings.PROBABILITIES['right']:
            self.quarter_turn(right)
        else:
            self.drive_straight(straight)

    def quarter_turn(self, direction):
        new_pos = self.LOC.update_car_pos_turn(self.to_dir, direction)

        if new_pos == self.position:
            # TODO: Handle out of bounds
            #logging.debug("quarter_turn: new pos is out-of-bounds, rejecting pos")
            return

        self.plan.put(
            {'command': 'quarter_turn', 'next_pos': new_pos, 'to_dir': direction,
             'from_dir': self.to_dir})

        self.prev_pos = self.position
        self.position = new_pos
        self.to_dir = direction

    def half_turn(self):
        self.plan.put({
            'command': 'half_turn', 'next_pos': self.position, 'to_dir': self.to_dir,
            'from_dir': Direction().inverse_dir(self.to_dir)
        })

    def drive_straight(self, direction):
        new_pos = self.LOC.update_car_pos(direction)

        if new_pos == self.position:
            self.handle_out_of_bounds()
            self.half_turn()
            return

        self.plan.put(
            {'command': 'straight', 'next_pos': new_pos, 'to_dir': direction,
             'from_dir': Direction().inverse_dir(direction)})

        self.prev_pos = self.position
        self.position = new_pos
        self.to_dir = direction

    def handle_out_of_bounds(self):
        new_pos = self.LOC.update_car_pos_turn(to_dir=self.to_dir, new_to_dir=Direction().inverse_dir(self.to_dir))
        self.to_dir = Direction().inverse_dir(self.to_dir)
        self.position = new_pos

    def stop_thread(self):
        self.exitFlag = True

