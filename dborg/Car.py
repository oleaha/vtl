import Location as Location
#import MotorControlMock as Mc
import MotorControl as Mc
import random
import time
import sys
from Utils import Direction


class CarEnhanced(object):
    DEBUG = True
    LOC = ''
    MC = ''

    car = {'ip': '', 'curr_pos': (), 'prev_pos': (), 'from_dir': '', 'to_dir': '', 'speed': 0}

    def __init__(self, ip, pos, from_dir, to_dir):
        self.car['ip'] = ip
        self.car['curr_pos'] = pos
        self.car['prev_pos'] = pos
        self.car['from_dir'] = from_dir
        self.car['to_dir'] = to_dir

        self.LOC = Location.Location(self.car['curr_pos'])
        self.MC = Mc.MotorControl()

        self.debug_car_info()

    def drive(self):
        num_iterations = 0
        while True:
            num_iterations += 1
            print "Iteration number: " + str(num_iterations)
            if self.LOC.closest_intersection(True) == 0:
                # If previous position was in intersection it is safe to assume that we don't need to turn.
                if not self.LOC.in_intersection(self.car['prev_pos']):
                    probability = random.uniform(0, 1)
                    if self.car['to_dir'] == Direction.SOUTH:
                        if probability <= 0.2:
                            self.quarter_turn(Direction.WEST)
                        elif probability <= 0.3:
                            self.quarter_turn(Direction.EAST)
                        else:
                            self.drive_straight(Direction.SOUTH)
                    elif self.car['to_dir'] == Direction.NORTH:
                        if probability <= 0.2:
                            self.quarter_turn(Direction.WEST)
                        elif probability <= 0.3:
                            self.quarter_turn(Direction.EAST)
                        else:
                            self.drive_straight(Direction.NORTH)
                    elif self.car['to_dir'] == Direction.WEST:
                        if probability <= 0.2:
                            self.quarter_turn(Direction.NORTH)
                        elif probability <= 0.3:
                            self.quarter_turn(Direction.SOUTH)
                        else:
                            self.drive_straight(Direction.WEST)
                    else:
                        if probability <= 0.2:
                            self.quarter_turn(Direction.NORTH)
                        elif probability <= 0.3:
                            self.quarter_turn(Direction.SOUTH)
                        else:
                            self.drive_straight(Direction.EAST)
                else:
                    self.drive_straight(self.car['to_dir'])
            else:
                self.drive_straight(self.car['to_dir'])

    def quarter_turn(self, new_dir):
        """
        Perform a quarter turn. It is important to use the direction the car is coming FROM and not where the car
        is currently going to, since this is basically what we change in this operation.
        """
        self.car['to_dir'] = new_dir
        self.car['prev_pos'] = self.car['curr_pos']

        self.debug_print("Performing quarter turn, coming from: "
                         + str(self.car['from_dir'] + " and turning: "
                               + str(self.car['to_dir'])))

        if not self.LOC.update_car_pos_turn(self.car['from_dir'], self.car['to_dir']):
            sys.exit()  # TODO: Handle OoB

        self.car['curr_pos'] = self.LOC.get_current_car_pos()
        self.car['from_dir'] = Direction().inverse_dir(self.car['to_dir'])

        self.debug_car_info()
        if self.DEBUG:
            time.sleep(1)

        if self.car['from_dir'] == Direction.SOUTH and self.car['to_dir'] == Direction.WEST:
            return self._perform_spin(-98)
        elif self.car['from_dir'] == Direction.NORTH and self.car['to_dir'] == Direction.WEST:
            return self._perform_spin(-98)
        elif self.car['from_dir'] == Direction.WEST and self.car['to_dir'] == Direction.SOUTH:
            return self._perform_spin(-98)
        elif self.car['from_dir'] == Direction.EAST and self.car['to_dir'] == Direction.NORTH:
            return self._perform_spin(-98)
        return self._perform_spin(98)

    def half_turn(self):
        """
        Usage: When robot reaches end of road, perform half
        :param direction:
        :return:
        """
        self.car['prev_pos'] = self.LOC.get_current_car_pos()

        print "Do turn"
        if not self.LOC.update_car_pos_turn(self.car['to_dir'], self.car['from_dir']):
            sys.exit()

        # Switch from with to
        self.car['from_dir'], self.car['to_dir'] = self.car['to_dir'], self.car['from_dir']
        self.car['curr_pos'] = self.LOC.get_current_car_pos()

        self.debug_car_info()
        self._perform_spin(-100)
        self._perform_spin(-0.05)
        self._perform_spin(-100)
        if self.DEBUG:
            time.sleep(1)

    def drive_straight(self, direction):
        self.car['prev_pos'] = self.car['curr_pos']

        if not self.LOC.update_car_pos(direction):
            self.half_turn()

        self.car['curr_pos'] = self.LOC.get_current_car_pos()
        self.debug_car_info()
        self._perform_drive(0.1)
        if self.DEBUG:
            time.sleep(1)

    def debug_car_info(self):
        self.debug_print("Prev pos: " + str(self.car['prev_pos']))
        self.debug_print("Current Position: " + str(self.car['curr_pos']))
        self.debug_print("Distance to intersection: " + str(self.LOC.closest_intersection(True)))
        self.debug_print("To Direction: " + str(self.car['to_dir']))
        self.debug_print("From direction: " + str(self.car['from_dir']))
        self.debug_print(self.LOC.print_map())
        return

    def debug_print(self, m):
        if self.DEBUG:
            print m

    def _perform_drive(self, meters):
        return self.MC.perform_drive(meters)

    def _perform_spin(self, angle):
        return self.MC.perform_spin(angle)


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

    def __init__(self, car_ip, initial_pos):
        self.IP = car_ip
        self.LOCATION = Location.Location(initial_pos)
        self.MOTOR_CONTROL = Mc.MotorControl()

        self.debug_print("SIM START...")
        self.debug_car_info()
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
                self.perform_move(self.direction())

    def direction(self):
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
        """
        Usage: When robot reaches end of road, perform half
        :param direction:
        :return:
        """
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


car = CarEnhanced('192.168.1.6', (20, 55), from_dir=Direction.WEST, to_dir=Direction.EAST)
car.drive()
