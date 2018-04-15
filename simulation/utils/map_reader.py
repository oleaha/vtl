import sys
import os
sys.path.append(os.getcwd())

from simulation.network.receive import Receive
from simulation.utils.message_types import MessageTypes
from simulation.environment.map import Map


class MapReader:
    running = False

    def __init__(self):
        self.receive = Receive("127.0.0.15")
        self.running = True
        self.location_table = {}
        self.map = Map()
        self.cars = []

        while self.running:
            msg = self.receive.listen()

            if msg['message_type'] == MessageTypes.BEACON:
                self.location_table[msg['ip']] = msg
                self.print_map()
                self.cars = []

    def stop(self):
        self.running = False

    def print_map(self):
        for ip, car in self.location_table.iteritems():
            self.cars.append((car['curr_pos'][0], car['curr_pos'][1]))

        print self.cars
        self.map.print_map(self.cars, "127.0.0.15")
