import threading, queue
import serial
import time
import os
import fcntl
import sys


plat = sys.platform.lower()
if plat[:5] == 'linux':
	TIOCSBRK = 0x5427
	TIOCCBRK = 0x5428
elif plat == 'cygwin':
	TIOCSBRK = 0x2000747B
	TIOCCBRK = 0x2000747A
elif plat[:3] == 'bsd' or \
plat[:7] == 'freebsd' or \
plat[:6] == 'netbsd' or \
plat[:7] == 'openbsd':
	TIOCSBRK = 0x2000747B
	TIOCCBRK = 0x2000747A
elif plat[:6] == 'darwin':   # OS X
	TIOCSBRK = 0x2000747B
	TIOCCBRK = 0x2000747A

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
		self.data = bytes((0,)*255)
		self.nextdata = None
		self.queue = queue.Queue(maxsize=1)
		self.timeout = 0


	def start(self):
		self.enabled = True
		self.send_thread = threading.Thread(target=self.sender)
		self.send_thread.daemon = True
		self.send_thread.start()

	def stop(self):
		self.enabled = False

	def sender(self):
		while True:
			if not(self.enabled):
				continue
			if os.name == "posix":
				# Linux does not have proper support for variable length breaks, as the behavior of TCSBRK is
				# undefined for values other than 0. (http://man7.org/linux/man-pages/man2/ioctl_tty.2.html)
				# Instead this controls the timing of the break directly.
				fcntl.ioctl(self.ser, TIOCSBRK)
				time.sleep(0.0001)
				fcntl.ioctl(self.ser,TIOCCBRK)
			else:
				self.ser.send_break(0.0001)
				
			if self.queue.empty() == False and self.timeout < time.time():
				(duration, self.data) = self.queue.get()
				self.timeout = time.time() + duration
				
			self.ser.write(bytes((0,)))
			self.ser.write(self.data)
			self.ser.flush()
			time.sleep(.1)
				
	def set_data(self, data, duration=0):
		self.queue.put((duration,data),block=True)

if __name__ == '__main__':
	sender = DMX_Serial("/dev/tty.usbserial-AD0JKV8Z")
	sender.start()

	while(1):
		sender.set_data(bytes((255,0,255,255) * 64))
