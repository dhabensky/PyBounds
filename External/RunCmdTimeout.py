import os
import time
import datetime
import threading
import subprocess


class RunCmd(threading.Thread):

	def __init__(self, cmd, progname):
		super(RunCmd, self).__init__()
		self.cmd = cmd
		self.progname = progname
		try:
			self.existing_pids = subprocess.check_output(["pidof", self.progname]).split()
		except:
			self.existing_pids = []
	pass

	def run(self):
		os.system(self.cmd)
	pass

	def stop(self):
		try:

			try:
				pids = subprocess.check_output(["pidof", self.progname]).split()
			except:
				pids = []

			for pid in self.existing_pids:
				try:
					pids.remove(pid)
				except:
					pass

			if len(pids) != 0:
				os.system("kill -15 " + " ".join(pids) + " 2>/dev/null")
		except:
			pass
		pass
	pass

pass  # RunCmd


class RunCmdTimeout:

	def __init__(self, cmd, progname, seconds):
		self.runcmd = RunCmd(cmd, progname)
		self.timeout = seconds
	pass

	def run(self):
		self.runcmd.start()
		start = datetime.datetime.now()
		delta = datetime.timedelta(0, self.timeout, 0)

		while self.runcmd.is_alive() and datetime.datetime.now() - start < delta:
			time.sleep(0.1)
		pass

		if self.runcmd.is_alive():
			self.runcmd.stop()
			return True
		else:
			return False
		pass
	pass

pass  # RunCmdTimeout
