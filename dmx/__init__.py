#!/usr/bin/python
import threading
import serial
import time

class DMX_Serial:
    def __init__(self, port="/dev/ttyUSB0"):
        if isinstance(port, str):
            self.ser = serial.Serial(port)
        else:
            self.ser = port
        self.ser.baudrate = 250000
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_TWO
        self.ser.xonoff = False
        self.enabled = False
        self.data = bytes((0,)*512)
        self.nextdata = None
        self.send_thread = threading.Thread(target=self.sender)
        self.send_thread.daemon = True
        self.send_thread.start()

    def start(self):
        self.enabled = True

    def stop(self):
        self.enabled = False

    def sender(self):
        while True:
            if not(self.enabled):
                continue
            self.ser.send_break(0.0001)
            self.ser.write(bytes((0,)))
            self.ser.write(self.data)
            self.ser.flush()
            if self.nextdata:
                self.data = self.nextdata
                self.nextdata = None

    def set_data(self, data):
        self.nextdata = data
