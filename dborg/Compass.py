import RPi.GPIO as GPIO
import smbus
import time
import math
import csv


class Compass(object):
    rev = GPIO.RPI_REVISION
    address = 0x1e
    bus = None

    # Variables
    scale = 0.92
    x_offset = 572.7
    y_offset = 451.3

    def __init__(self):
        if self.rev == 2 or self.rev == 3:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = smbus.SMBus(0)

        self._write_byte(0, 0b01110000)
        self._write_byte(1, 0b00100000)
        self._write_byte(2, 0b00000000)

    def get_compass_value(self):
        x = (self._read_word_2c(3) - self.x_offset) * self.scale
        y = (self._read_word_2c(7) - self.y_offset) * self.scale
        return [x, y]

    def _read_byte(self, adr):
        return self.bus.read_byte_data(self.address, adr)

    def _read_word(self, adr):
        high = self.bus.read_byte_data(self.address, adr)
        low = self.bus.read_byte_data(self.address, adr + 1)
        return (high << 8) + low

    def _read_word_2c(self, adr):
        val = self._read_word(adr)
        if val >= 0x8000:
            return -(65535 - val) + 1
        return val

    def _write_byte(self, adr, value):
        self.bus.write_byte_data(self.address, adr, value)

    def calibrate_compass(self):
        # TODO: Implement easy calibration process
        pass
