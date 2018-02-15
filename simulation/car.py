import sys
import os
sys.path.append(os.getcwd())


from simulation.location.location import Location
#from simulation.piborg.motorControl import MotorControl
from simulation.piborg.motorControlMock import MotorControl
from simulation.planner.planner import Planner
from simulation.network.send import Send
from simulation.network.receive import Receive
import settings

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
        # Initialize motor control module
        self.MC = MotorControl()

        # Create a queue for commands planned by the planner
        self.plan = Queue.Queue()
        # Initialize and start planner
        self.PLANNER = Planner(1, "Planner", self.car['curr_pos'], self.car['to_dir'], self.plan)
        self.PLANNER.start()

        # Initialize network module and send beacon method
        self.beacon_thread = threading.Thread(target=self.send_beacon, name="Send Beacon")  # TODO: No sure if this is the best solution
        self.beacon_thread.start()

        # Initialize network receive message module
        self.receive_thread = threading.Thread(target=self.receive, name="Receive")
        self.receive_thread.start()

        while True:
            if self.plan.qsize() > 5:
                # TODO: self.plan.get does not include
                self.next_command = self.plan.get()
                logging.debug("Command: " + str(self.next_command))
                time.sleep(1)  # TODO: The time will depend on current command.

                # TODO: Implement MotorControl and update self.car

    def send_beacon(self):
        """
        Sends a beacon broadcast message every with car info every x seconds.
        """
        send = Send(broadcast=True)
        while True:
            logging.debug("Sending beacon")
            send.send(self.car)
            time.sleep(settings.BROADCAST_STEP)

    def receive(self):
        receive = Receive(self.car['ip'])
        while True:
            msg = receive.listen()
            logging.info("Message received")

            # Throw away updates from yourself
            if not self.car['ip'] == msg['ip']:
                self.location_table[msg['ip']] = msg
                logging.info("Updated location table " + str(self.location_table))


if len(sys.argv) > 1:
    c = Car(str(sys.argv[1]), (19, 19), 'e', 'w')
else:
    c = Car('192.168.1.1', (19, 19), 'e', 'w')
