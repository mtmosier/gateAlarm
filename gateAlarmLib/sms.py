from gateAlarmLib import pygvoicelib
from twilio.rest import TwilioRestClient
import smtplib
from datetime import datetime, timedelta


class Sms:
	clientGV = None
	clientTwilio = None
	_adminEmailObj = None
	_fromNumber = None
	_gvThrottleTimedelta = None
	_gvRetryGracePeriodTimedelta = None
	_gvLastMessageSent = None
	_gvLocked = False


	def __init__(self, config, adminEmailObj = None):
		self._adminEmailObj = adminEmailObj

		if 'GoogleVoice' in config:
			username = config['GoogleVoice']['Username']
			appPass = config['GoogleVoice']['AppPass']

			if 'ThrottleTimeInSeconds' in config['GoogleVoice']:
				self._gvThrottleTimedelta = timedelta(seconds=float(config['GoogleVoice']['ThrottleTimeInSeconds']))
			else:
				self._gvThrottleTimedelta = timedelta(seconds=0)

			if 'RetryGracePeriodInMinutes' in config['GoogleVoice']:
				self._gvRetryGracePeriodTimedelta = timedelta(minutes=float(config['GoogleVoice']['RetryGracePeriodInMinutes']))
			else:
				self._gvRetryGracePeriodTimedelta = timedelta(seconds=0)

		if Sms.clientGV is None and 'GoogleVoice' in config:
			Sms.clientGV = pygvoicelib.GoogleVoice(username, appPass)
			Sms.clientGV.validate_credentials()

		if Sms.clientTwilio is None and 'Twilio' in config:
			accountSid = config['Twilio']['AccountSid']
			authToken = config['Twilio']['AuthToken']
			self._fromNumber = config['Twilio']['FromNumber']

			Sms.clientTwilio = TwilioRestClient(accountSid, authToken)

	def exit(self):
		pass

	def sendSms(self, phoneNumber, message):
		smsSent = False

		if Sms.clientGV is not None:
			if self._gvLocked and (self._gvLastMessageSent is None or self._gvLastMessageSent < (datetime.today() - self._gvRetryGracePeriodTimedelta)):
				self._gvLocked = False

			if not self._gvLocked and (self._gvLastMessageSent is None or self._gvLastMessageSent < (datetime.today() - self._gvThrottleTimedelta)):
				if not Sms.clientGV.sms(phoneNumber, message):
					self._gvLocked = True
					if self._gvLastMessageSent is None:
						self._gvLastMessageSent = datetime.today()

					if self._adminEmailObj is not None:
						self._adminEmailObj.sendEmail('Google Voice sms is failing for GateAlarm', '')

				else:
					smsSent = True
					self._gvLastMessageSent = datetime.today()

		if not smsSent and Sms.clientTwilio is not None:
			try:
				Sms.clientTwilio.messages.create(to=phoneNumber, from_=self._fromNumber, body=message)
				smsSent = True
			except twilio.TwilioRestException as e:
				pass

		return smsSent
