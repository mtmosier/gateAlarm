from gateAlarmLib.gateAlarm import GateAlarm



gateAlarm = GateAlarm('/etc/gateAlarm.conf')
try:
	gateAlarm.run()
except KeyboardInterrupt:
	print("Interrupt found.  Exiting.")
except:
	raise
finally:
	gateAlarm.exit()

