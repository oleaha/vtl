import socket, sys
from simulation import settings
import logging
import json
import struct


class Send:

    def __init__(self, broadcast=False, ip=None, port=None):
        if broadcast:
            self.ip = settings.BROADCAST_IP
            if port:
                self.port = port
            else:
                self.port = settings.BROADCAST_PORT
        else:
            self.ip = ip
            self.port = port

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except socket.error:
            logging.error("Could not create socket, error: " + str(socket.error.message))

    def send(self, msg_type, msg):
        try:
            msg['message_type'] = msg_type
            self.socket.sendto(json.dumps(msg), (self.ip, self.port))
        except socket.error:
            logging.error("Could not send message")

    def close(self):
        self.socket.close()


class SendMulticast:

    def __init__(self, broadcast=False, ip=None, port=None):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
        except socket.error:
            logging.error("Could not create socket, error: " + str(socket.error.message))

    def send(self, msg_type, msg):
        try:
            msg['message_type'] = msg_type
            self.socket.sendto(json.dumps(msg), (settings.MULTICAST_GROUP_IP, settings.MULTICAST_PORT))
        except socket.error:
            logging.error("Could not send message")

    def close(self):
        self.socket.close()