import time as t
import threading
import sys
import Location as Loc
import Network as Net
import MotorControl as MC

class Car(object):
    ME = ''
    GPS = ''
    RECEIVE = ''
    SEND = ''
    MOTOR_CONTROL = ''
    VTL = ''

    def __init__(self, car):
        if car == 1:
            self.ME = '192.168.1.6'
            self.GPS = Loc.Location(0, 20, 1)
        elif car == 2:
            self.ME = '192.168.1.7'
            self.GPS = Loc.Location(19, 0, 1)
        else:
            self.ME = '192.168.1.12'
            self.GPS = Loc.Location(40, 0, 1)

        self.RECEIVE = Net.Receive()
        self.SEND = Net.Send(8888)
        self.VTL = Light()
        self.MOTOR_CONTROL = MC.MotorControl()

    def main(self, car):
        t1 = threading.Thread(target=self.RECEIVE)
        t2 = threading.Thread(target=self.startLight, args=(0, 1, 1, 1))
        t1.start()

        if car == 1:
            self.loop_one()
        else:
            self.loop_two()

        # self.RECEIVE.ACTIVE = False
        # self.MOTOR_CONTROL.PBR.MotorsOff()
        # sys.exit()

    def send(self, message):
        self.SEND.send_packet(message)

    def receive(self):
        self.RECEIVE.bind(8888)
        while self.RECEIVE.ACTIVE:
            d = self.RECEIVE.listen()
            self.messageHandler(d)

    def message_factory(self, message_type):
        if message_type == 1:
            m = str(message_type) + ":" + str(self.GPS.my_pos[1] + ":" + str(self.GPS.my_pos[0]))
            return m
        elif message_type == 2:
            m = str(message_type) + ":" + str(self.GPS.my_pos[1] + ":" + str(self.GPS.my_pos[0]))
            return m
        elif message_type == 3:
            m = str(message_type) + ":" + str(self.intersection_id) + ":" + str(self.state_one) + ":" \
                + str(self.state_three) + ":" + str(self.state_four)
            print m
            return m
        elif message_type == 4:
            distance = self.GPS.distance_to_intersection()
            m = str(message_type) + ":" + str(self.GPS.my_pos[1]) + ":" + str(self.GPS.my_pos[0]) + ":" \
                + str(distance[0]) + str(distance[1]) + str(distance[2]) + str(distance[3])
            print m
            return m
        elif message_type == 5:
            m = str(message_type) + ":" + str(self.GPS.my_pos[1]) + ":" + str(self.GPS.my_pos[0])
            t2.start()  # TODO: WTF?!
            return m
        return

    @staticmethod
    def str_to_bool(str):
        if str == "True":
            return True
        return False

    def do_move(self, direction):
        distance = self.GPS.distance_to_intersection()
        self.GPS.draw_map()

        if distance[0] === 1 and not self.state_me:
            while not self.state_me:
                print "Stopping"
                t.sleep(0.5)
        elif distance[0] < 10: # and not leaving
            print "approaching"
        else:
            print "far away"

        self.GPS.update_pos(direction)
        self.send(self.message_factory(4))
        self.MOTOR_CONTROL.perform_drive(-0.1)

    def do_turn(self, direction):
        # self.GPS.draw_map()
        self.GPS.update_pos(direction)
        self.send(self.message_factory(4))
        self.MOTOR_CONTROL.perform_spin(-100)
        self.MOTOR_CONTROL.perform_spin(-0.05)
        self.MOTOR_CONTROL.perform_spin(-100)

    def loop_one(self):
        while True:
            for i in range(60):
                self.do_move('r')
            self.do_turn('u')
            for i in range(60):
                self.do_move('l')
            self.do_turn('d')

    def loop_two(self):
        while True:
            for i in range(39):
                self.do_move('d')
            self.do_turn('r')
            for i in range(39):
                self.do_move('u')
            self.do_turn('l')


    STATE_ONE = ['010', 2]
    STATE_TWO = ['100', 10]
    STATE_THREE = ['110', 2]
    STATE_FOUR = ['001', 10]
    state_one = False
    state_two = False
    state_three = False
    state_four = False
    intersection_id = None
    state_me = None

    def leader_election(self):
        #clusterMe
        #clusterYou
        return

    def is_leaving(self):
        return False

    def is_green(self, lights):
        my_direction = self.GPS.distance_to_intersection()

        if my_direction[1]:
            self.state_one = self.str_to_bool(lights[0])
            self.state_three = self.str_to_bool(lights[1])
            self.state_two = self.str_to_bool(lights[2])
            self.state_four = self.str_to_bool(lights[3])
            self.state_me = self.str_to_bool(lights[my_direction[2]])

    def start_light(self, intersection_id, state, cluster_me, cluster_you):
        self.state_one = False
        self.state_two = False
        self.state_three = False
        self.state_four = False
        self.intersection_id = intersection_id

        my_direction = self.GPS.distance_to_intersection()[2]
        if my_direction == 1 or my_direction == 3:
            odd =True
        else:
            odd = False

        self.STATE_TWO[1] = cluster_me * 3
        self.STATE_FOUR[1] = cluster_you * 3
        # while True
        state = int(state) % 4

        if state == 0:
            self.state_one = False
            self.state_two = False
            self.state_three = False
            self.state_three = False
            self.send(self.message_factory(3))
            t.sleep(self.STATE_ONE[1])
            t.sleep(2)
            state += 1
        elif state == 1:
            if odd:
                self.state_one = False
                self.state_two = True
                self.state_three = False
                self.state_four = True
            else:
                self.state_one = True
                self.state_two = False
                self.state_three = True
                self.state_four = False

            self.send(self.message_factory(3))
            crossing_cars = True

            while crossing_cars:
                t.sleep(self.STATE_TWO[1])
                crossing_cars = False
            state += 1
        elif state == 2:
            self.state_one = False
            self.state_two = False
            self.state_three = False
            self.state_three = False
            self.send(self.message_factory(3))
            t.sleep(self.STATE_ONE[1])
            state += 1
        elif state == 3:
            if odd:
                self.state_one = False
                self.state_two = True
                self.state_three = False
                self.state_four = True
            else:
                self.state_one = True
                self.state_two = False
                self.state_three = True
                self.state_four = False

            self.send(self.message_factory(3))
            crossing_cars = True
            while crossing_cars:
                t.sleep(self.STATE_FOUR[1])
                crossing_cars = False
            t.sleep(2)
            state += 1

if __name__ == '__main__':
    my_car = Car(1)
    my_car.main(1)













