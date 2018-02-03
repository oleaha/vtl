from simulation.location.location import Location
#from simulation.piborg.motorControl import MotorControl
from simulation.piborg.motorControlMock import MotorControl
from simulation.planner.planner import Planner

import logging
import Queue


class Car:

    LOC = None
    MC = None
    PLANNER = None

    car = {'ip': '', 'curr_pos': (), 'prev_pos': (), 'from_dir': '', 'to_dir': '', 'speed': 0}
    location_table = {}  # Table of all active robots

    def __init__(self, ip, pos, from_dir, to_dir):
        self.car['ip'] = ip
        self.car['curr_pos'] = pos
        self.car['prev_pos'] = pos
        self.car['to_dir'] = to_dir
        self.car['from_dir'] = from_dir
        # Thread logger
        logging.basicConfig(level=logging.INFO,
                            format='[%(relativeCreated)6d %(threadName)s - %(funcName)21s():%(lineno)s ] : %(message)s',
                            filename="log.txt")
        logging.debug("car.py started")

        # Initialize location module
        self.LOC = Location(self.car['curr_pos'])
        #self.LOC.map.print_map(pos)
        self.MC = MotorControl()

        self.plan = Queue.Queue()

        self.PLANNER = Planner(1, "Planner", self.car['curr_pos'], self.car['to_dir'], self.plan)
        self.PLANNER.start()

        while True:
            if self.plan.qsize() > 5:
                #logging.debug("Command: " + str(self.plan.get()))
                self.plan.get()
                #time.sleep(0.1)


                #self.PLANNER.stop_thread()


c = Car('192.168.1.1.', (19, 19), 'e', 'w')
