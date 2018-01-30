from simulation.location.location import Location
#from simulation.piborg.motorControl import MotorControl
from simulation.piborg.motorControlMock import MotorControl


class Car:

    LOC = None
    MC = None

    car = {'ip': '', 'curr_pos': (), 'prev_pos': (), 'from_dir': '', 'to_dir': '', 'speed': 0}
    location_table = {}  # Table of all active robots

    def __init__(self, ip, pos, from_dir, to_dir):
        self.car['ip'] = ip
        self.car['curr_pos'] = pos
        self.car['prev_pos'] = pos
        self.car['to_dir'] = to_dir
        self.car['from_dir'] = from_dir

        # Initialize location module
        self.LOC = Location(self.car['curr_pos'])
        self.MC = MotorControl()

        self.LOC.map.print_map(self.car['curr_pos'])


c = Car('192.168.1.1.', (12, 24), 'e', 'w')
