#!/usr/bin/python

import RPi.GPIO as GPIO
import smbus
import time


class Compass():

    rev = GPIO.RPI_REVISION
    bus = ''
    address = ''

    def __init__(self):
        if self.rev == 2 or self.rev == 3:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = smbus.SMBus(0)

        self.address = 0x1e

    def read_word(self, adr):
        high = self.bus.read_byte_data(self.address, adr)
        low = self.bus.read_byte_data(self.address, adr+1)
        val = (high << 8) + low
        return val

    def read_word_2c(self, adr):
        val = self.read_word(adr)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def write_byte(self, adr, value):
        self.bus.write_byte_data(self.address, adr, value)

    def get_value(self):
        self.write_byte(0, 0b01110000)  # Set to 8 samples @ 15Hz
        self.write_byte(1, 0b00100000)  # 1.3 gain LSb / Gauss 1090 (default)
        self.write_byte(2, 0b00000000)  # Continuous sampling

        scale = 0.92
        x_offset = 572.7
        y_offset = 451.3
        while True:
            x_out = (self.read_word_2c(3) - x_offset) * scale
            y_out = (self.read_word_2c(7) - y_offset) * scale
            z_out = (self.read_word_2c(5)) * scale
            print "X: " + str(x_out) + " Y: " + str(y_out)
            time.sleep(0.2)
            return [x_out, y_out]
