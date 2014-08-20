import http.client, urllib
import json
import smtplib
from datetime import datetime, timedelta
from gateAlarmLib.adminEmail import AdminEmail


class PushMessage:
	_adminEmailObj = None
	_apiToken = None
	_retryGracePeriodTimedelta = None
	_host = None
	_urlPath = None
	_lastMessageSent = None
	_locked = False
	_defaultTitle = None

	def __init__(self, config, adminEmailObj = None):
		self._adminEmailObj = adminEmailObj
		if 'Pushover' in config:
			self._apiToken = config['Pushover']['ApiToken']
			self._host = config['Pushover']['Host']
			self._urlPath = config['Pushover']['UrlPath']

			if 'DefaultTitle' in config['Pushover']:
				self._defaultTitle = config['Pushover']['DefaultTitle']

			if 'RetryGracePeriodInMinutes' in config['Pushover']:
				self._retryGracePeriodTimedelta = timedelta(minutes=float(config['Pushover']['RetryGracePeriodInMinutes']))
			else:
				self._retryGracePeriodTimedelta = timedelta(seconds=0)

	def exit(self):
		pass

	def sendMessage(self, userID, message, title = None, priority = None):
		messageSent = False

		if self._apiToken is not None:
			if self._locked and (self._lastMessageSent is None or self._lastMessageSent < (datetime.today() - self._retryGracePeriodTimedelta)):
				self._locked = False

			if not self._locked:
				if title is None:
					title = self._defaultTitle

				params = {
					"token": self._apiToken,
					"user": userID,
					"message": message,
				}
				if title is not None:
					params["title"] = title
				if priority is not None:
					params["priority"] = priority

				conn = http.client.HTTPSConnection(self._host)
				conn.request("POST", self._urlPath, urllib.parse.urlencode(params), { "Content-type": "application/x-www-form-urlencoded" })
				output = conn.getresponse().read().decode('utf-8')
				data = json.loads(output)

				if data['status'] != 1:
					self._locked = True
					if self._lastMessageSent is None:
						self._lastMessageSent = datetime.today()

					errorMessages = ''
					for error in data['errors']:
						errorMessages += error + "\n"
					errorMessages = errorMessages.rstrip()

					if self._adminEmailObj is not None:
						self._adminEmailObj.sendEmail('Pushover is failing for GateAlarm', errorMessages)

				else:
					messageSent = True
					self._lastMessageSent = datetime.today()

		return messageSent
