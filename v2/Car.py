import Location as Location
import MotorControlMock as Mc
# import MotorControl as Mc
import random
import time
import sys


class Direction:
    NORTH = 'n'
    SOUTH = 's'
    WEST = 'w'
    EAST = 'e'


class Car(object):
    DEBUG = True
    # Network

    # Current car
    IP = ''
    LOCATION = ''
    PREV_POS = (0, 20)
    MOTOR_CONTROL = ''

    # Constants
    CAR_IPS = ['192.168.1.6', '192.168.1.7', '192.168.1.12']
    CAR_INITIAL_POSITIONS = [(16, 19), (19, 0), (40, 0)]

    def __init__(self, car_id):
        self.IP = self.CAR_IPS[car_id - 1]
        self.LOCATION = Location.Location(self.CAR_INITIAL_POSITIONS[car_id - 1])
        self.MOTOR_CONTROL = Mc.MotorControl()
        self.debug_print(self.LOCATION.print_map())

    def drive(self):
        while True:
            if self.LOCATION.closest_intersection(True) == 0:
                if not self.LOCATION.in_intersection(self.PREV_POS):
                    probability = random.uniform(0, 1)
                    direction = self.direction()

                    if direction == Direction.SOUTH:
                        if probability <= 0.8:
                            self.quarter_turn(Direction.WEST)
                        elif probability <= 0.98:
                            self.quarter_turn(Direction.EAST)
                        else:
                            self.perform_move(Direction.SOUTH)
                    elif direction == Direction.NORTH:
                        if probability <= 0.2:
                            self.quarter_turn(Direction.WEST)
                        elif probability <= 0.3:
                            self.quarter_turn(Direction.EAST)
                        else:
                            self.perform_move(Direction.NORTH)
                    elif direction == Direction.WEST:
                        if probability <= 0.2:
                            self.quarter_turn(Direction.NORTH)
                        elif probability <= 0.3:
                            self.quarter_turn(Direction.SOUTH)
                        else:
                            self.perform_move(Direction.WEST)
                    else:
                        if probability <= 0.2:
                            self.quarter_turn(Direction.NORTH)
                        elif probability <= 0.3:
                            self.quarter_turn(Direction.SOUTH)
                        else:
                            self.perform_move(Direction.EAST)
                else:
                    self.perform_move(self.direction())
            else:
                # TODO: This should not be hard coded
                self.perform_move(Direction.SOUTH)

    def direction(self):
        # TODO: First decision should not be hard coded
        current_pos = self.LOCATION.get_current_car_pos()
        if current_pos[0] - self.PREV_POS[0] > 0:
            return Direction.SOUTH
        elif current_pos[0] - self.PREV_POS[0] < 0:
            return Direction.NORTH
        elif current_pos[1] - self.PREV_POS[1] > 0:
            return Direction.WEST
        else:
            return Direction.EAST

    def perform_move(self, direction):
        self.PREV_POS = self.LOCATION.get_current_car_pos()

        if not self.LOCATION.update_car_pos(direction):
            # TODO: Handle out of bounds
            sys.exit()

        self.debug_car_info()
        self._perform_drive(0.1)
        if self.DEBUG:
            time.sleep(1)

    def half_turn(self, direction):
        self.PREV_POS = self.LOCATION.get_current_car_pos()
        if not self.LOCATION.update_car_pos(direction):
            # TODO: Handle out of bounds
            sys.exit()
        self.debug_car_info()
        self._perform_spin(-100)
        self._perform_spin(-0.05)
        self._perform_spin(-100)
        if self.DEBUG:
            time.sleep(1)

    def quarter_turn(self, direction):
        from_dir = self.direction()
        print "Performing turn, changing direction from " + str(from_dir) + " to " + str(direction)
        self.PREV_POS = self.LOCATION.get_current_car_pos()
        if not self.LOCATION.update_car_pos_turn(from_dir, direction):
            # TODO: Handle out of bounds
            sys.exit()
        self.debug_car_info()
        if self.DEBUG:
            time.sleep(1)

        if from_dir == Direction.EAST:
            if direction == Direction.NORTH:
                return self._perform_spin(-98)
            return self._perform_spin(98)
        if from_dir == Direction.WEST:
            if direction == Direction.NORTH:
                return self._perform_spin(98)
            return self._perform_spin(-98)
        if from_dir == Direction.NORTH:
            if direction == Direction.WEST:
                return self._perform_spin(-98)
            return self._perform_spin(98)
        if from_dir == Direction.SOUTH:
            if direction == Direction.SOUTH:
                return self._perform_spin(-98)
            return self._perform_spin(98)

    def debug_car_info(self):
        self.debug_print("Prev pos: " + str(self.PREV_POS))
        self.debug_print("Current Position: " + str(self.LOCATION.get_current_car_pos()))
        self.debug_print("Distance to intersection: " + str(self.LOCATION.closest_intersection(True)))
        self.debug_print("Direction: " + str(self.direction()))
        self.debug_print(self.LOCATION.print_map())
        return

    def debug_print(self, m):
        if self.DEBUG:
            print m

    def _perform_spin(self, angle):
        return self.MOTOR_CONTROL.perform_spin(angle)

    def _perform_drive(self, meters):
        return self.MOTOR_CONTROL.perform_drive(meters)

car = Car(1)
car.drive()
