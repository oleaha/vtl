import PicoBorgRev
import time
import sys
from simulation.piborg import ThunderBorg
from simulation.camera.lane import LaneDetection
import logging
import Queue
import numpy
from simulation import settings

class MotorControlV2:
    """
    Class for DiddyBorg V2, requires ThunderBorg.py
    """

    def __init__(self):
        # Set up thunderborg
        self.TB = ThunderBorg.ThunderBorg()
        self.TB.Init()

        self.measurements = Queue.LifoQueue()
        logging.debug("Starting LaneDetection Thread")
        self.LD = LaneDetection(self.measurements)
        self.LD.start()

        if not self.TB.foundChip:
            boards = ThunderBorg.ScanForThunderBorg()

            if len(boards) == 0:
                print "No ThunderBorg found, check that you are attached :)"
            else:
                print "No ThunderBorg at address %02X, but we did find boards:" % self.TB.i2cAddress
                for board in boards:
                    print '     %02X (%d)' % (board, board)
                print "You need to change the I2C address. Change the setup line so it is correct"
                print "TB.i2cAddress = 0x%02X" % (boards[0])
            sys.exit()

        self.TB.SetCommsFailsafe(False)
        self.timeForwardOneMeter = 3.15

        self.timeSpinThreeSixty = 2.37
        self.voltageIn = 12.0
        self.voltageOut = 0.95 * 12

        if self.voltageOut > self.voltageIn:
            self.maxPower = 1.0
        else:
            self.maxPower = self.voltageOut / float(self.voltageIn)

    def perform_move(self, drive_left, drive_right, num_seconds):
        self.TB.SetMotor1(-drive_left * self.maxPower)
        self.TB.SetMotor2(drive_right * self.maxPower)
        time.sleep(num_seconds)
        self.TB.SetMotor1(0)
        self.TB.SetMotor2(0)
        time.sleep(0.3)

    def perform_spin(self, angle):
        if angle < 0.0:
            # Left turn
            drive_left = -1.0
            drive_right = 1.0
            angle *= -1
        else:
            # Right turn
            drive_left = 1.0
            drive_right = -1.0

        self.LD.perform_ld(value=False)
        num_seconds = (angle / 360.0) * self.timeSpinThreeSixty
        self.perform_move(drive_left, drive_right, num_seconds)

    def perform_drive(self, meters, use_lane_detection=True):
        self.LD.perform_ld(value=True)
        if meters < 0.0:
            drive_left = -1.0
            drive_right = -1.0
            meters *= -1
        else:
            drive_left = 1.0
            drive_right = 1.0

        # TODO: Implement adjustment, only when driving straight and before straight command.
        logging.info("Lane detection queue size:" + str(self.measurements.qsize()))
        if use_lane_detection and self.measurements.qsize() > 0:
            measure = self.measurements.get()

            if len(measure) > 0:
                measure = [x for x in measure if x > 0]
                if len(measure) > 0:
                    average = numpy.average(measure)
                    if average < settings.ACTUAL_CENTER:
                        drive_left = drive_left * 0.95
                    elif average > settings.ACTUAL_CENTER:
                        drive_right = drive_right * 0.95
            self.measurements.task_done()

        num_seconds = meters * self.timeForwardOneMeter
        self.perform_move(drive_left, drive_right, num_seconds)

    def stop_motors(self):
        self.TB.MotorsOff()

    def set_led_green(self):
        self.TB.SetLeds(0, 1, 0)

    def set_led_red(self):
        self.TB.SetLeds(1, 0, 0)

    def set_led_yellow(self):
        self.TB.SetLeds(1, 0.5, 0)

    def stop_lane_detection(self):
        self.LD.stop_thread()


class MotorControlV1(object):
    """
    Class for DiddyBorg V1, requires PicoBorgRev.py
    """

    def __init__(self):
        # Set up PicoBorg Reverse
        self.PBR = PicoBorgRev.PicoBorgRev()
        self.PBR.Init()

        if not self.PBR.foundChip:
            self.boards = PicoBorgRev.ScanForPicoBorgReverse()

            if len(self.boards) == 0:
                print "No PicoBorg Reverse found, check connection"
            else:
                print "No PivoBorg Reverse at address \%02X, but we did find boards: " + str(self.PBR.i2cAddress)

                # TODO: Check this in documentation, reference 16
            sys.exit()

        self.PBR.SetCommsFailsafe(False)
        self.PBR.ResetEpo()

        # Movement settings
        self.timeForwardOneMeter = 8.2
        self.timeSpinThreeSixty = 4.88
        # Power settings
        self.voltageIn = 12.0 # Total battery voltage
        self.voltageOut = 6.0 # Max motor voltage

        # Set power limits
        if self.voltageOut > self.voltageIn:
            self.maxPower = 1.0
        else:
            self.maxPower = self.voltageOut / float(self.voltageIn)

    def perform_move(self, drive_left, drive_right, num_seconds):
        percent = 0.8
        speed = self.maxPower * percent

        self.PBR.SetMotor1(drive_right * speed)
        self.PBR.SetMotor2(-drive_left * speed)

        # Wait
        time.sleep(num_seconds)
        self.PBR.MotorsOff()

    # Sin an angle in degrees
    def perform_spin(self, angle):
        if angle < 0.0: # Left turn
            drive_left = -1.0
            drive_right = 1.0
            angle *= -1
        else: # Right turn
            drive_left = 1.0
            drive_right = -1.0

        # Calc time needed
        num_seconds = (angle / 360.0) * self.timeSpinThreeSixty
        # Perform move
        self.perform_move(drive_left, drive_right, num_seconds)

    def perform_drive(self, meters):
        if meters < 0.0: # Reverse
            drive_left = -1.0
            drive_right = -1.0
            meters *= -1
        else: # Forward
            drive_left = +1
            drive_right = +1

        num_seconds = meters*self.timeForwardOneMeter
        self.perform_move(drive_left, drive_right, num_seconds)
