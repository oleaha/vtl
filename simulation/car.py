
import sys
import os
sys.path.append(os.getcwd())

from simulation.location.location import Location
from simulation.piborg.motorControl import MotorControlV2
#from simulation.piborg.motorControlMock import MotorControlV2
from simulation.planner.planner import Planner
from simulation.network.send import Send, SendMulticast
from simulation.network.receive import Receive, ReceiveMulticast
import settings
from simulation.utils.direction import Direction
from simulation.utils.message_types import MessageTypes
from simulation.utils.utils import calculate_quarter_spin_degree

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
    traffic_light_state = {}
    plan = None
    beacon_thread = None
    receive_thread = None
    statistics = {}

    def __init__(self, ip, pos, from_dir, to_dir, use_traffic_light=False):
        self.car['ip'] = ip
        self.car['curr_pos'] = pos
        self.car['prev_pos'] = pos
        self.car['to_dir'] = to_dir
        self.car['from_dir'] = from_dir
        self.next_command = None
        self.RUNNING = True
        self.use_traffic_light = use_traffic_light
        self.statistics['wait_time'] = 0
        self.statistics['number_of_steps'] = 0
        self.statistics['number_of_crossings'] = 0
        self.statistics['total_simulation_time'] = 0

        self.init_simulation()

        self.LOC.map.print_map([self.car['curr_pos']], self.car['ip'])

        self.simulation_thread()

    def simulation_thread(self):
        start = 0
        try:
            start = time.time()
            while True:
                # TODO: REGULAR TRAFFIC LIGHT!
                if self.plan.qsize() > 5 and len(self.traffic_light_state) > 0:
                    self.execute_command()
                    self.LOC.map.print_map([self.car['curr_pos']], self.car['ip'])
                    #time.sleep(2)
                    logging.info("---------")
        except KeyboardInterrupt:
            self.statistics['total_simulation_time'] = time.time() - start
            self.statistics['average_speed'] = ((self.statistics['number_of_steps'] * settings.DRIVE_STEP) / 100) / self.statistics['total_simulation_time']

            logging.info("STATISTICS: " + str(self.statistics))

            self.PLANNER.stop_thread()
            self.MC.stop_motors()
            self.MC.stop_lane_detection()
            self.RUNNING = False
            logging.debug("All systems stopped")
            sys.exit()

    def init_simulation(self):
        # Thread logger
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s ; %(threadName)s - %(funcName)21s():%(lineno)s ] ; %(message)s',
                            filename='log_' + str(self.car['ip']) + '.log', datefmt="%Y-%m-%d %H:%M:%S"
                            )
        logging.debug("car.py started")

        # Initialize location module
        # TODO: Remember that only one car has this feature!
        self.LOC = Location(self.car['curr_pos'], use_traffic_light=self.use_traffic_light)
        # Initialize motor control module
        self.MC = MotorControlV2()

        # Create a queue for commands planned by the planner
        self.plan = Queue.Queue()
        # Initialize and start planner
        self.PLANNER = Planner(1, "Planner", self.car['curr_pos'], self.car['to_dir'], self.plan)
        self.PLANNER.start()

        self.beacon_thread = threading.Thread(target=self._send_beacon,
                                              name="Send Beacon")  # TODO: No sure if this is the best solution
        self.beacon_thread.start()

        # Initialize network receive message module
        self.receive_thread = threading.Thread(target=self._receive, name="Receive")
        self.receive_thread.start()

    def execute_command(self):
        self.next_command = self.plan.get()
        logging.error("1: Next command to execute: " + str(self.next_command))

        while not self.is_next_pos_available():
            logging.error("2: Next position is not available, waiting")
            time.sleep(0.5)
        """
        Start regular traffic light implementation
        """
        if self.LOC.is_next_pos_in_intersection(self.next_command['next_pos']) and not self.LOC.is_next_pos_in_intersection(self.car['curr_pos']):
            logging.error("3: Next pos is intersection")
            intersection = self.LOC.get_intersection(self.next_command['next_pos'])
            intersection_id = sum(map(sum, intersection.get_pos()))

            if intersection_id in self.traffic_light_state:
                traffic_light = self.traffic_light_state[intersection_id]

                if self.next_command['from_dir'] == Direction.NORTH:
                    while True:
                        if self.traffic_light_state[intersection_id]['state'] == "0" or self.traffic_light_state[intersection_id]['state'] == "1":
                            break
                        logging.error("Waiting from green light from north or south")
                        self.statistics['wait_time'] += 1
                        time.sleep(1)
                elif self.next_command['from_dir'] == Direction.SOUTH:
                    while True:
                        if self.traffic_light_state[intersection_id]['state'] == "0" or self.traffic_light_state[intersection_id]['state'] == "1":
                            break
                        logging.error("Waiting from green light from north or south")
                        self.statistics['wait_time'] += 1
                        time.sleep(1)
                elif self.next_command['from_dir'] == Direction.EAST:
                    while True:
                        if self.traffic_light_state[intersection_id]['state'] == "2" or self.traffic_light_state[intersection_id]['state'] == "3":
                            break
                        logging.error("Waiting from green light from east or west")
                        self.statistics['wait_time'] += 1
                        time.sleep(1)
                elif self.next_command['from_dir'] == Direction.WEST:
                    while True:
                        if self.traffic_light_state[intersection_id]['state'] == "2" or self.traffic_light_state[intersection_id]['state'] == "3":
                            break
                        logging.error("Waiting from green light from east or west")
                        self.statistics['wait_time'] += 1
                        time.sleep(1)
                self.statistics['number_of_crossings'] += 1
        """
        End regular traffic light implementation
        """

        if self.next_command['command'] == "straight":
            logging.error("4: Executing straight command")
            self.statistics['number_of_steps'] += 1
            self.MC.perform_drive(settings.DRIVE_STEP)

        elif self.next_command['command'] == "quarter_turn":
            logging.error("5: Executing quarter turn command")
            from_dir = self.next_command['from_dir']
            to_dir = self.next_command['to_dir']
            turn = ""
            if from_dir == Direction.WEST:
                if to_dir == Direction.SOUTH:
                    turn = "left"
                else:
                    turn = "right"
            if from_dir == Direction.SOUTH:
                if to_dir == Direction.EAST:
                    turn = "left"
                else:
                    turn = "right"
            if from_dir == Direction.EAST:
                if to_dir == Direction.NORTH:
                    turn = "left"
                else:
                    turn = "right"
            if from_dir == Direction.NORTH:
                if to_dir == Direction.WEST:
                    turn = "left"
                else:
                    turn = "right"
            if turn == "right":
                self.MC.perform_spin(calculate_quarter_spin_degree(
                        from_dir=self.next_command['from_dir'],
                        to_dir=self.next_command['to_dir']
                    ))
                self.MC.perform_drive(settings.DRIVE_STEP)
                self.statistics['number_of_steps'] += 1
            else:
                logging.debug("6: Turning LEFT")
                self.MC.perform_drive(settings.DRIVE_STEP)
                self.MC.perform_spin(calculate_quarter_spin_degree(
                    from_dir=self.next_command['from_dir'],
                    to_dir=self.next_command['to_dir']
                ))
                self.MC.perform_drive(settings.DRIVE_STEP)
                self.statistics['number_of_steps'] += 1

        elif self.next_command['command'] == "half_turn":
            logging.error("7: Executing half turn command")
            self.MC.perform_spin(-90)
            self.MC.perform_drive(0.25, use_lane_detection=False)
            self.MC.perform_spin(-90)
            time.sleep(2)
        self.update_self_state()

    def is_next_pos_available(self):
        if len(self.location_table) > 0:
            for ip, location in self.location_table.iteritems():
                #logging.error("Other car current pos: " + str(location['curr_pos']) + " My next pos: " + str(self.next_command['next_pos']))
                if tuple(location['curr_pos']) == self.next_command['next_pos']:
                    logging.error("NEXT POS IS NOT AVAILABLE")
                    return False
        return True

    def message_handler(self, msg_type, msg):

        if msg_type == MessageTypes.BEACON:
            # Update location table with new data
            if msg['ip'] != self.car['ip']:
                self.location_table[msg['ip']] = msg
                #logging.error("Updated location table " + str(self.location_table))

        if msg_type == MessageTypes.TRAFFIC_LIGHT:
            # message is coming here
            i_id = sum(map(sum, msg['intersection']))
            #logging.error(msg)
            self.traffic_light_state[i_id] = msg

    def update_self_state(self):
        self.car['prev_pos'] = self.car['curr_pos']
        self.car['curr_pos'] = self.next_command['next_pos']
        self.car['to_dir'] = self.next_command['to_dir']
        self.car['from_dir'] = self.next_command['from_dir']

    def _send_beacon(self):
        """
        Sends a beacon broadcast message every with car info every x seconds.
        """
        send = SendMulticast(broadcast=True)
        while self.RUNNING:
            send.send(MessageTypes.BEACON, self.car)
            time.sleep(settings.BROADCAST_STEP)
        logging.debug("Shutting down sender")
        send.close()

    def _receive(self):
        """
        Listens for broadcast messages on the network. Update location table if sender is not the same as receiver
        :return:
        """
        receive = ReceiveMulticast(self.car['ip'])
        while self.RUNNING:
            msg = receive.listen()
            self.message_handler(msg['message_type'], msg)
        logging.debug("Shutting down receiver")
        receive.close()


if len(sys.argv) > 1:
    if sys.argv[2] == "True":
        traffic_light = True
    else:
        traffic_light = False
    c = Car(str(sys.argv[1]), (3, 11), 'e', 'w', traffic_light)
else:
    c = Car('192.168.1.1', (3, 7), 'e', 'w', False)
