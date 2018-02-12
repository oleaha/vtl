import socket
import logging
from simulation import settings


class Receive:

    def __init__(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((settings.BROADCAST_IP, settings.BROADCAST_PORT))
        except socket.error:
            logging.error("Could not create socket, error: " + str(socket.error))

    def listen(self):
        logging.debug("Listening...")
        return self.socket.recvfrom(1024)

    def close(self):
        self.socket.close()
