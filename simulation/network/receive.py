import socket
import logging
from simulation import settings
import json


class Receive:

    def __init__(self, ip):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((ip, settings.BROADCAST_PORT))

        except socket.error, msg:
            logging.error("Could not create socket, error: " + str(msg))

    def listen(self):
        logging.debug("Listening...")
        return json.loads(self.socket.recvfrom(1024)[0])

    def close(self):
        self.socket.close()
