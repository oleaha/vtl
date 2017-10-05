import Location as Location
import MotorControl as Mc
import random


class Car(object):
    DEBUG = False
    # Network

    # Current car
    IP = ''
    LOCATION = ''
    PREV_POS = (0, 20)
    MOTOR_CONTROL = ''

    # Constants
    CAR_IPS = ['192.168.1.6', '192.168.1.7', '192.168.1.12']
    CAR_INITIAL_POSITIONS = [(1, 20), (19, 0), (40, 0)]

    def __init__(self, car_id):
        self.IP = self.CAR_IPS[car_id - 1]
        self.LOCATION = Location.Location(self.CAR_INITIAL_POSITIONS[car_id - 1])
        self.MOTOR_CONTROL = Mc.MotorControl()
        self.debug_print(self.LOCATION.print_map())

    def drive(self):
        while True:
            if self.LOCATION.closest_intersection(True) == 0:
                probability = random.uniform(0, 1)
                direction = self.direction()

                if direction == 's':
                    if probability <= 0.2:
                        self.quarter_turn('w')
                    elif probability <= 0.3:
                        self.quarter_turn('e')
                    else:
                        self.perform_move('s')
                elif direction == 'n':
                    if probability <= 0.2:
                        self.quarter_turn('w')
                    elif probability <= 0.3:
                        self.quarter_turn('e')
                    else:
                        self.perform_move('n')
                elif direction == 'w':
                    if probability <= 0.2:
                        self.perform_move('n')
                    elif probability <= 0.3:
                        self.perform_move('s')
                    else:
                        self.perform_move('w')
                else:
                    if probability <= 0.2:
                        self.perform_move('n')
                    elif probability <= 0.3:
                        self.perform_move('s')
                    else:
                        self.perform_move('e')
            else:
                self.perform_move('s')

    # TODO: Something is not working here, the initial position is fucking up
    def direction(self):
        current_pos = self.LOCATION.get_current_car_pos()
        print "Current pos: " + str(current_pos) + " - Prev pos: " + str(self.PREV_POS)
        if current_pos[0] - self.PREV_POS[0] > 0:
            return 's'
        elif current_pos[0] - self.PREV_POS[0] < 0:
            return 'n'
        elif current_pos[1] - self.PREV_POS[1] > 0:
            return 'w'
        else:
            return 'e'

    def perform_move(self, direction):
        self.PREV_POS = self.LOCATION.get_current_car_pos()
        self.LOCATION.update_car_pos(direction)
        self.MOTOR_CONTROL.perform_drive(0.1)

    def half_turn(self, direction):
        self.LOCATION.update_car_pos(direction)
        self.MOTOR_CONTROL.perform_spin(-100)
        self.MOTOR_CONTROL.perform_spin(-0.05)
        self.MOTOR_CONTROL.perform_spin(-100)

    def quarter_turn(self, direction):
        from_dir = self.direction()
        self.LOCATION.update_car_pos(direction)

        if from_dir == 'e':
            if direction == 'n':
                return self.MOTOR_CONTROL.perform_spin(-98)
            return self.MOTOR_CONTROL.perform_spin(98)
        if from_dir == 'w':
            if direction == 'n':
                return self.MOTOR_CONTROL.perform_spin(98)
            return self.MOTOR_CONTROL.perform_spin(-98)
        if from_dir == 'n':
            if direction == 'w':
                return self.MOTOR_CONTROL.perform_spin(-98)
            return self.MOTOR_CONTROL.perform_spin(98)
        if from_dir == 's':
            if direction == 'e':
                return self.MOTOR_CONTROL.perform_spin(-98)
            return self.MOTOR_CONTROL.perform_spin(98)

    def debug_car_info(self):
        self.debug_print("Prev pos: " + str(self.PREV_POS))
        self.debug_print("Car Position: " + str(self.LOCATION.get_current_car_pos()))
        self.debug_print("Distance to intersection: " + str(self.LOCATION.closest_intersection(True)))
        self.debug_print(self.LOCATION.print_map())

    def debug_print(self, m):
        if self.DEBUG:
            print m
