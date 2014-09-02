from time import sleep
from datetime import datetime
import wiringpi2 as wiringpi
from threading import Lock




class Sensor:
	_watchPin = None
	_triggerEnded = None
	_lastStatus = None
	_dataLock = None
	_triggerOnHigh = None
	_name = None
	_timeMarker = None
	_timeMarker2 = None

	def __init__(self, name, pinToWatch, triggerOnHigh = True):
		self._watchPin = pinToWatch
		self._dataLock = Lock()
		self._name = name
		self._triggerOnHigh = triggerOnHigh

		wiringpi.wiringPiSetupGpio()
		wiringpi.piHiPri(99)
		wiringpi.wiringPiISR(self._watchPin, wiringpi.GPIO.INT_EDGE_BOTH, Sensor.gpioCallback, self)

		if bool(wiringpi.digitalRead(self._watchPin)) == self._triggerOnHigh:
			self._lastStatus = True
		else:
			self._lastStatus = False
			self._triggerEnded = datetime.today()

	def gpioCallback(self):
		if bool(wiringpi.digitalRead(self._watchPin)) == self._triggerOnHigh:
			with self._dataLock:
				self._lastStatus = True
		else:
			with self._dataLock:
				if self._lastStatus:
					self._lastStatus = False
					self._triggerEnded = datetime.today()


	def exit(self):
		pass

	def setTimeMarker(self, timeMarker):
		self._timeMarker = timeMarker

	def getTimeMarker(self):
		return self._timeMarker

	def setTimeMarker2(self, timeMarker2):
		self._timeMarker2 = timeMarker2

	def getTimeMarker2(self):
		return self._timeMarker2

	def getName(self):
		return self._name

	def checkSensor(self):
		with self._dataLock:
			return self._lastStatus

	def getTimeTriggerEnded(self):
		with self._dataLock:
			if self._lastStatus:
				return False
			return self._triggerEnded



if __name__ == '__main__':

	sensor = Sensor('FrontGate', 18)

	try:
		while True:
			if sensor.checkSensor():
				print("Sensor Triggered!")
			else:
				print("No sensor trigger since", sensor.getTimeTriggerEnded())
			sleep(5)
	except:
		raise
	finally:
		sensor.exit()
