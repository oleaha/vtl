import socket
import sys


class Receive(object):
    HOST = ''
    PORT = ''
    s = ''

    _ACTIVE = False

    def get_active(self):
        return self._ACTIVE

    def set_active(self, state):
        self._ACTIVE = state

    ACTIVE = property(get_active, set_active)

    def __init__(self):
        self.HOST = ''
        self.ACTIVE = True

    def set_port(self, port):
        self.PORT = port

    def bind(self, port):
        self.set_port(port)

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print "Socket created!"
        except socket.error, msg:
            print "Failed to create socket. Error Code: " + str(msg[0]) + " Message " + str(msg[1])
            sys.exit()

        print "Socket binding complete"

    def listen(self):
        d = self.s.recvfrom(1024)

        if d[0].strip() == 'quit':
            self.ACTIVE = False
        return d

    def close(self):
        self.s.close()


class Send(object):
    HOST = ''
    PORT = ''
    s = ''

    def __init__(self, port):
        self.host = '192.168.1.255'
        self.PORT = port

        # create datagram UDP socket
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except socket.error:
            print "Failed to create socket"
            sys.exit()

    def send_packet(self, message):
        try:
            self.s.sendto(message, (self.HOST, self.PORT))
        except socket.error, message:
            print "Error Code: " + str(message[0]) + " Message: " + str(message[1])
            sys.exit()

    def close(self):
        self.s.close()