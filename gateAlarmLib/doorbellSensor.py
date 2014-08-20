from time import sleep
from datetime import datetime, timedelta
import wiringpi2 as wiringpi
from threading import Lock




class DoorbellSensor:
	_watchPin = None
	_timeLastTriggered = None
	_dataLock = None
	_triggerOnHigh = None
	_name = None
	_timeMarker = None
	_debounceTimedelta = None

	def __init__(self, name, pinToWatch, triggerOnHigh = True, debounceTimeInSeconds = 0):
		self._watchPin = pinToWatch
		self._dataLock = Lock()
		self._name = name
		self._triggerOnHigh = triggerOnHigh
		self._debounceTimedelta = timedelta(seconds=debounceTimeInSeconds)

		wiringpi.wiringPiSetupGpio()
		wiringpi.piHiPri(99)
		wiringpi.wiringPiISR(self._watchPin, wiringpi.GPIO.INT_EDGE_BOTH, DoorbellSensor.gpioCallback, self)

		if bool(wiringpi.digitalRead(self._watchPin)) == self._triggerOnHigh:
			self._timeLastTriggered = datetime.today()

	def gpioCallback(self):
		if bool(wiringpi.digitalRead(self._watchPin)) == self._triggerOnHigh:
			with self._dataLock:
				if self._timeLastTriggered is None or self._timeLastTriggered < (datetime.today() - self._debounceTimedelta):
					self._timeLastTriggered = datetime.today()

	def exit(self):
		pass

	def setTimeMarker(self, timeMarker):
		self._timeMarker = timeMarker

	def getTimeMarker(self):
		return self._timeMarker

	def getName(self):
		return self._name

	def getTimeLastTriggered(self):
		with self._dataLock:
			return self._timeLastTriggered



if __name__ == '__main__':

	sensor = DoorbellSensor('Front Doorbell', 25)

	try:
		while True:
			if sensor.getTimeLastTriggered() is not None:
				print("Sensor last triggered", sensor.getTimeLastTriggered())
			sleep(5)
	except:
		raise
	finally:
		sensor.exit()
