import Location as Location
import MotorControl as Mc


class Car(object):
    DEBUG = True
    # Network

    # Current car
    IP = ''
    LOCATION = ''
    PREV_POS = ''
    MOTOR_CONTROL = ''

    # Constants
    CAR_IPS = ['192.168.1.6', '192.168.1.7', '192.168.1.12']
    CAR_INITIAL_POSITIONS = [(0, 20), (19, 0), (40, 0)]

    def __init__(self, car_id):
        self.IP = self.CAR_IPS[car_id - 1]
        self.LOCATION = Location.Location(self.CAR_INITIAL_POSITIONS[car_id - 1])
        self.MOTOR_CONTROL = Mc.MotorControl()
        self.debug_print(self.LOCATION.print_map())

    def drive(self):
        for i in range(60):
            self.PREV_POS = self.LOCATION.get_current_car_pos()
            self.LOCATION.update_car_pos('n')
            self.MOTOR_CONTROL.perform_drive(0.1)
            self.debug_print(self.LOCATION.get_current_car_pos())
            self.debug_print(self.LOCATION.print_map())

    def debug_print(self, m):
        if self.DEBUG:
            print m
