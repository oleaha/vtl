import time
from simulation import settings


class TrafficLight:

    def __init__(self, intersection=((), ())):
        self.current_state = False  # False = RED, True = Green
        self.intersection = intersection
        self.start = 0
        self.stop = 0

        self.exitFlag = False

    def start_timer(self):
        self.start = time.time()

    def get_time_difference(self):
        return time.time() - self.start

    def stop_traffic_light_thread(self):
        self.exitFlag = not self.exitFlag

    # TODO: Send messages for each iteration. Which intersection (position) and state, broadcast
    def operate(self):
        self.start_timer()
        while not self.exitFlag:
            if self.get_time_difference() < settings.TRAFFIC_LIGHT_INTERVAL:
                if self.current_state:
                    print "Light is GREEN"
                else:
                    print "Light is RED"
            else:
                if self.current_state:
                    print "Change to RED light"
                else:
                    print "Change to GREEN light"

                self.start_timer()
                self.current_state = not self.current_state
            time.sleep(1)


