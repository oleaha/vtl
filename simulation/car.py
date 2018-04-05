
import sys
import os
sys.path.append(os.getcwd())

from simulation.location.location import Location
from simulation.piborg.motorControl import MotorControlV2
#from simulation.piborg.motorControlMock import MotorControlV2
from simulation.planner.planner import Planner
from simulation.network.send import Send
from simulation.network.receive import Receive
import settings
from simulation.utils.direction import Direction
from simulation.utils.message_types import MessageTypes

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
        self.next_command = None
        self.RUNNING = True

        # Thread logger
        logging.basicConfig(level=logging.INFO,
                            format='[%(relativeCreated)6d %(threadName)s - %(funcName)21s():%(lineno)s ] : %(message)s',
                            )
        logging.debug("car.py started")

        # Initialize location module
        self.LOC = Location(self.car['curr_pos'])
        # Initialize motor control module
        self.MC = MotorControlV2()

        # Create a queue for commands planned by the planner
        self.plan = Queue.Queue()
        # Initialize and start planner
        self.PLANNER = Planner(1, "Planner", self.car['curr_pos'], self.car['to_dir'], self.plan)
        self.PLANNER.start()

        self.beacon_thread = threading.Thread(target=self.send_beacon, name="Send Beacon")  # TODO: No sure if this is the best solution
        self.beacon_thread.start()

        # Initialize network receive message module
        self.receive_thread = threading.Thread(target=self.receive, name="Receive")
        self.receive_thread.start()

        self.LOC.map.print_map(self.car['curr_pos'], self.car['ip'])

        try:
            while True:
                if self.plan.qsize() > 5:
                    self.execute_command()
                    self.LOC.map.print_map(self.car['curr_pos'], self.car['ip'])
                    logging.info("---------")
        except KeyboardInterrupt:
            self.PLANNER.stop_thread()
            self.MC.stop_motors()
            self.MC.stop_lane_detection()
            self.RUNNING = False
            logging.debug("All systems stopped")
            sys.exit()

    def execute_command(self):
        self.next_command = self.plan.get()
        logging.error("Next command to execute: " + str(self.next_command))

        if self.next_command['command'] == "straight":
            logging.error("Executing straight command")
            self.MC.perform_drive(0.2)
        elif self.next_command['command'] == "quarter_turn":
            logging.error("Executing quarter turn command")
            self.MC.perform_spin(self.calculate_quarter_spin_degree())
            # TODO: When turning left, go one step up, then 90 degree turn
        elif self.next_command['command'] == "half_turn":
            logging.error("Executing half turn command")
            self.MC.perform_spin(-90)
            self.MC.perform_drive(0.21)
            self.MC.perform_spin(-90)
        self.update_self_state()

    def update_self_state(self):
        self.car['prev_pos'] = self.car['curr_pos']
        self.car['curr_pos'] = self.next_command['next_pos']
        self.car['to_dir'] = self.next_command['to_dir']
        self.car['from_dir'] = self.next_command['from_dir']

    # TODO: Refactor to UTILS
    def calculate_quarter_spin_degree(self):
        from_dir = self.next_command['from_dir']
        to_dir = self.next_command['to_dir']

        if from_dir == Direction.WEST:
            if to_dir == Direction.NORTH:
                return settings.QUARTER_TURN_DEGREES
            return -settings.QUARTER_TURN_DEGREES
        elif from_dir == Direction.EAST:
            if to_dir == Direction.SOUTH:
                return settings.QUARTER_TURN_DEGREES
            return -settings.QUARTER_TURN_DEGREES
        elif from_dir == Direction.NORTH:
            if to_dir == Direction.WEST:
                return settings.QUARTER_TURN_DEGREES
            return -settings.QUARTER_TURN_DEGREES
        else:
            if to_dir == Direction.EAST:
                return settings.QUARTER_TURN_DEGREES
            return -settings.QUARTER_TURN_DEGREES

    def message_handler(self, msg_type, msg):
        if msg_type == MessageTypes.BEACON:
            # Update location table with new data
            self.location_table[msg['ip']] = msg
            logging.info("Updated location table " + str(self.location_table))

    def send_beacon(self):
        """
        Sends a beacon broadcast message every with car info every x seconds.
        """
        send = Send(broadcast=True)
        while self.RUNNING:
            logging.debug("Sending beacon")
            send.send(MessageTypes.BEACON, self.car)
            time.sleep(settings.BROADCAST_STEP)
        send.close()

    def receive(self):
        """
        Listens for broadcast messages on the network. Update location table if sender is not the same as receiver
        :return:
        """
        receive = Receive(self.car['ip'])
        while self.RUNNING:
            msg = receive.listen()

            # Skip messages where sender is the same as receiver
            if msg['ip'] != self.car['ip']:
                self.message_handler(msg['message_type'], msg)

        receive.close()


if len(sys.argv) > 1:
    c = Car(str(sys.argv[1]), (3, 7), 'e', 'w')
else:
    c = Car('192.168.1.1', (3, 7), 'e', 'w')
