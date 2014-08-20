import smtplib


class AdminEmail:
	_adminEmail = None
	_emailLoginUser = None
	_emailLoginPassword = None


	def __init__(self, config):
		if 'AdminEmail' in config['General']:
			self._adminEmail = config['General']['AdminEmail']
		if 'EmailLoginUser' in config['General']:
			self._emailLoginUser = config['General']['EmailLoginUser']
		if 'EmailLoginPassword' in config['General']:
			self._emailLoginPassword = config['General']['EmailLoginPassword']

	def exit(self):
		pass

	def sendEmail(self, subject, body):
		if self._adminEmail is not None and self._emailLoginUser is not None:
			emailMessage = '\r\n'.join(['To: ' + self._adminEmail, 'From: ' + self._emailLoginUser, 'Subject: ' + subject, body, ''])

			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.ehlo()
			server.starttls()
			server.login(self._emailLoginUser, self._emailLoginPassword)

			try:
				server.sendmail(self._emailLoginUser, self._adminEmail, emailMessage)
			except:
				pass

			server.quit()
