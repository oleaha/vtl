import time
from simulation import settings
from simulation.network.send import Send
import threading

from simulation.utils.message_types import MessageTypes


class TrafficLight:

    def __init__(self, intersection=((), ())):
        self.current_state = 0  # False = RED, True = Green

        """
        Traffic light states:
        0 - Allow cars approaching FROM North to drive
        1 - Allow cars approaching FROM South to drive
        2 - Allow cars approaching FROM East to drive
        3 - Allow cars approaching FROM West to drive
        The current state indicates which lane has the right to drive
        """

        self.intersection = intersection
        self.timer = 0
        self.stop = 0
        self.exitFlag = False
        self.send = threading.Thread(target=self.operate, name="Regular Traffic Light")
        self.send.start()

    def start_timer(self):
        self.timer = time.time()

    def get_time_difference(self):
        return time.time() - self.timer

    def stop_traffic_light_thread(self):
        self.exitFlag = not self.exitFlag

    def create_message(self, color):
        return {
            'state': str(self.current_state),
            "color": color,
            'intersection': self.intersection
        }

    def operate(self):
        self.start_timer()
        send = Send(broadcast=True, port=settings.BROADCAST_PORT)
        while not self.exitFlag:
            # Only change to/from when timer exceeds the interval
            if self.get_time_difference() >= settings.TRAFFIC_LIGHT_INTERVAL:
                # Send out a yellow light
                send.send(MessageTypes.TRAFFIC_LIGHT, self.create_message("yellow"))

                # Allow cars to exit the intersection
                time.sleep(settings.TRAFFIC_LIGHT_YELLOW_DURATION)

                # Restart the timer and increment the current state
                self.start_timer()
                self.current_state = (self.current_state + 1) % 4

            # Inform which lane has green light
            send.send(MessageTypes.TRAFFIC_LIGHT, self.create_message("green"))
            time.sleep(settings.TRAFFIC_LIGHT_INTERVAL)

        send.close()

    def stop(self):
        self.exitFlag = False
