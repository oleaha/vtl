from simulation.location.location import Location
#from simulation.piborg.motorControl import MotorControl
from simulation.piborg.motorControlMock import MotorControl
from simulation.planner.planner import Planner
from simulation.network.send import Send

import logging
import Queue
import time
import threading
import json

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
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(relativeCreated)6d %(threadName)s - %(funcName)21s():%(lineno)s ] : %(message)s',
                            )
        logging.debug("car.py started")

        # Initialize location module
        self.LOC = Location(self.car['curr_pos'])
        self.MC = MotorControl()

        # Initialize and start planner module
        self.plan = Queue.Queue()
        self.PLANNER = Planner(1, "Planner", self.car['curr_pos'], self.car['to_dir'], self.plan)
        self.PLANNER.start()

        # Initialize network module
        self.beacon_thread = threading.Thread(target=self.send_beacon())  # TODO: No sure if this is the best solution
        self.beacon_thread.start()


        while True:
            if self.plan.qsize() > 5:
                #logging.debug("Command: " + str(self.plan.get()))
                time.sleep(1)


                #self.PLANNER.stop_thread()

    def send_beacon(self):
        send = Send(broadcast=True)
        while True:
            logging.debug("Sending beacon")
            send.send(json.dumps(self.car))
            time.sleep(1)


c = Car('192.168.1.1.', (19, 19), 'e', 'w')
