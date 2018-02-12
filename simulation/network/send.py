import socket, sys
from simulation import settings
import logging


class Send:

    def __init__(self, broadcast=False):
        if broadcast:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            except socket.error:
                logging.error("Could not create socket, error: " + str(socket.error))

            self.ip = settings.BROADCAST_IP
            self.port = settings.BROADCAST_PORT

    def send(self, msg):
        try:
            self.socket.sendto(msg, (self.ip, self.port))
        except socket.error:
            logging.error("Could not send message")

    def close(self):
        self.socket.close()