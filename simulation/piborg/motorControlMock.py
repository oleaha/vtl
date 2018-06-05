import time


class MotorControlV2(object):

    def __init__(self):
        return

    def perform_move(self, drive_left=None, drive_right=None, num_seconds=None):
        time.sleep(2)
        return

    # Sin an angle in degrees
    def perform_spin(self, angle):
        return self.perform_move()

    def perform_drive(self, meters, use_lane_detection=True):
        return self.perform_move()

    def stop_motors(self):
        return

    def stop_lane_detection(self):
        pass
