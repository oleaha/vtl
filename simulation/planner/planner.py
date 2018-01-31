import time
import threading
from simulation.location.location import Location


class Planner(threading.Thread):

    def __init__(self, threadId, name, location):
        """
        :type location: Location
        """
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.name = name
        self.exitFlag = False
        self.route = []
        self.location = location

    def run(self):
        print "Starting thread: " + self.name
        self.planner()
        print "Exiting thread: " + self.name

    def planner(self):
        while not self.exitFlag:
            if len(self.route) < 6:
                self.calculate_next_step()

    def calculate_next_step(self):
        self.route.append(self.location.get_car_pos())
        print(self.location.get_car_pos())


    def stop_thread(self):
        self.exitFlag = True

