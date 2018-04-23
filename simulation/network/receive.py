import socket
import logging
from simulation import settings
import json
import struct


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


class ReceiveMulticast:
    def __init__(self, ip):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('', 10000))

            self.group = socket.inet_aton(settings.MULTICAST_GROUP_IP)
            mreq = struct.pack('4sL', self.group, socket.INADDR_ANY)
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except socket.error, msg:
            logging.error("Could not create socket, error: " + str(msg))

    def listen(self):
        logging.debug("Listening...")
        return json.loads(self.socket.recvfrom(1024)[0])

    def close(self):
        self.socket.close()
