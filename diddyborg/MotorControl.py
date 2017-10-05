import PicoBorgRev
import time
import sys


class MotorControl(object):

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
