import os
from pwd import getpwnam
from grp import getgrnam
import configparser
from time import sleep
from datetime import datetime, timedelta
from gateAlarmLib.sensor import Sensor
from gateAlarmLib.doorbellSensor import DoorbellSensor
from gateAlarmLib.sms import Sms
from gateAlarmLib.adminEmail import AdminEmail
from gateAlarmLib.pushMessage import PushMessage




class GateAlarm:

	# ----------------------------------------------------------------------
	# Private Data Members

	_phoneNumberList = []
	_pushNotificationList = []
	_sensorObjList = []
	_doorbellObj = None
	_smsObj = None
	_pushMessageObj = None
	_sensorTriggerGracePeriodTimedelta = None
	_sensorTriggerLongPeriodTimedelta = None
	_sendGateClosedMessage = False
	_debug = False


	def __init__(self, configFilePath):
		config = configparser.ConfigParser()
		config.read('/etc/gateAlarm.conf')

		if 'Debug' in config['General']:
			self._debug = config['General'].getboolean('Debug')

		if self._debug:
			print("starting initialization")

		if 'Sensors' in config:
			for sensorName in config['Sensors']:
				if not sensorName.lower().endswith('_triggeronhigh'):
					sensorPin = int(config['Sensors'][sensorName])
					triggerOnHigh = True
					if sensorName + '_TriggerOnHigh' in config['Sensors']:
						triggerOnHigh = config['Sensors'].getboolean(sensorName + '_TriggerOnHigh')

					sensorName = self.convertCase(sensorName)
					sensorObj = Sensor(sensorName, sensorPin, triggerOnHigh)
					self._sensorObjList.append(sensorObj)

					if self._debug:
						print("sensor created using " + sensorName + ", " + str(sensorPin) + ", " + str(triggerOnHigh))

		if 'Doorbell' in config:
			debounceInSeconds = 0
			if 'DoorbellDebounceInSeconds' in config['Alarm']:
				debounceInSeconds = float(config['Alarm']['DoorbellDebounceInSeconds'])

			for doorbellName in config['Doorbell']:
				doorbellPin = int(config['Doorbell'][doorbellName])
				triggerOnHigh = True
				if doorbellName + '_TriggerOnHigh' in config['Doorbell']:
					triggerOnHigh = config['Doorbell'].getboolean(doorbellName + '_TriggerOnHigh')

				doorbellName = self.convertCase(doorbellName)
				self._doorbellObj = DoorbellSensor(doorbellName, doorbellPin, triggerOnHigh, debounceInSeconds)

				if self._debug:
					print("doorbell created using " + doorbellName + ", " + str(doorbellPin) + ", " + str(triggerOnHigh) + ", " + str(debounceInSeconds))

		if self._debug:
			print("finished creating sensor objects")

		# after setup of sensor objects is complete drop root privileges
		user = config['General']['User']
		userId = getpwnam(user).pw_uid

		groups = config['General']['Group'].split(',')
		groupIds = []
		for group in groups:
			groupIds.append(getgrnam(group).gr_gid)

		os.setgroups(groupIds)
		os.setgid(groupIds[0])
		os.setuid(userId)
		os.umask(0o007)

		# complete setup after root is dropped
		adminEmailObj = AdminEmail(config)
		self._smsObj = Sms(config, adminEmailObj)
		self._pushMessageObj = PushMessage(config, adminEmailObj)

		if 'SensorGracePeriodInSeconds' in config['Alarm']:
			self._sensorTriggerGracePeriodTimedelta = timedelta(seconds=float(config['Alarm']['SensorGracePeriodInSeconds']))
		else:
			self._sensorTriggerGracePeriodTimedelta = timedelta(seconds=0)

		if 'SensorLongGracePeriodInSeconds' in config['Alarm']:
			self._sensorTriggerLongPeriodTimedelta = timedelta(seconds=float(config['Alarm']['SensorLongGracePeriodInSeconds']))

		if 'SendGateClosedMessage' in config['Alarm']:
			self._sendGateClosedMessage = config['Alarm'].getboolean('SendGateClosedMessage')

		if 'PhoneNumbers' in config:
			for name in config['PhoneNumbers']:
				self._phoneNumberList.append(config['PhoneNumbers'][name])

		if 'PushNotificationUsers' in config:
			for userID in config['PushNotificationUsers']:
				self._pushNotificationList.append(config['PushNotificationUsers'][userID])

		if self._debug:
			print("initialization complete")

	def convertCase(self, input):
		output = ' '.join([ x.capitalize() for x in input.split('_') ])
		return output

	def exit(self):
		if self._smsObj is not None:
			if self._debug:
				print("exiting sms object")
			self._smsObj.exit()

		for sensorObj in self._sensorObjList:
			if self._debug:
				print("exiting sensor object")
			sensorObj.exit()

		if self._debug:
			print("exit complete")

	def checkSensor(self, sensorObj):
		if not sensorObj.checkSensor():
			triggerEndedTime = sensorObj.getTimeTriggerEnded()
			if triggerEndedTime < (datetime.today() - self._sensorTriggerGracePeriodTimedelta):
				if triggerEndedTime != sensorObj.getTimeMarker():
					sensorObj.setTimeMarker(triggerEndedTime)
					for userID in self._pushNotificationList:
						self._pushMessageObj.sendMessage(userID, sensorObj.getName() + ' is open')
					for phoneNumber in self._phoneNumberList:
						self._smsObj.sendSms(phoneNumber, sensorObj.getName() + ' is open')
					if self._debug:
						print("message sent saying " + sensorObj.getName() + " is open")

			if self._sensorTriggerLongPeriodTimedelta is not None and triggerEndedTime < (datetime.today() - self._sensorTriggerLongPeriodTimedelta):
				if triggerEndedTime != sensorObj.getTimeMarker2():
					sensorObj.setTimeMarker2(triggerEndedTime)
					for userID in self._pushNotificationList:
						self._pushMessageObj.sendMessage(userID, sensorObj.getName() + ' is still open', None, 2)
					for phoneNumber in self._phoneNumberList:
						self._smsObj.sendSms(phoneNumber, sensorObj.getName() + ' is still open')
					if self._debug:
						print("message sent saying " + sensorObj.getName() + " is still open")

		else:
			if sensorObj.getTimeMarker() is not None:
					sensorObj.setTimeMarker(None)
					sensorObj.setTimeMarker2(None)
					if self._sendGateClosedMessage:
						for userID in self._pushNotificationList:
							self._pushMessageObj.sendMessage(userID, sensorObj.getName() + ' is now closed')
						for phoneNumber in self._phoneNumberList:
							self._smsObj.sendSms(phoneNumber, sensorObj.getName() + ' is now closed')
						if self._debug:
							print("message sent saying " + sensorObj.getName() + " is closed")

	def checkDoorbell(self):
		if self._doorbellObj is not None:
			lastTrigger = self._doorbellObj.getTimeLastTriggered()
			if lastTrigger is not None:
				lastMessageSent = self._doorbellObj.getTimeMarker()
				if lastMessageSent is None or lastMessageSent < lastTrigger:
					self._doorbellObj.setTimeMarker(datetime.today())
					for userID in self._pushNotificationList:
						self._pushMessageObj.sendMessage(userID, self._doorbellObj.getName() + ' rung')
					for phoneNumber in self._phoneNumberList:
						self._smsObj.sendSms(phoneNumber, self._doorbellObj.getName() + ' rung')
					if self._debug:
						print("message sent saying " + self._doorbellObj.getName() + " has been rung")

	def run(self):
		while True:
			self.checkDoorbell()

			for sensorObj in self._sensorObjList:
				self.checkSensor(sensorObj)

			sleep(0.33)




if __name__ == '__main__':
	gateAlarm = GateAlarm('/etc/gateAlarm.conf')
	try:
		gateAlarm.run()
	except KeyboardInterrupt:
		print("Interrupt found.  Exiting.")
	except:
		raise
	finally:
		gateAlarm.exit()

