import os
import time
import datetime
import threading
import subprocess




def debug_print(s, name_log):
	directory = "/home/max/TestFile/"
	directory += name_log
	format_file = ".txt"
	directory += format_file

	ffff = open(directory, 'a')
	ffff.write(s)
	ffff.write('\n')
	ffff.close()

def check_num(s):
	s_res = ''	
	for i in s:
		if(i >= '0' and i <= '9' or i == ' '):
			s_res += i	
	return s_res

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
		# print(self.cmd)
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

			# print(pids)
			if len(pids) != 0:	
				pids_str = ' '.join(str(i) for i in pids)
				pids_str = check_num(pids_str)
				# print(pids_str)			
				os.system("kill -9 " + pids_str + " 2>/dev/null")
		except Exception as ex:			
			print(str(ex))
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

		if self.runcmd.is_alive():
			self.runcmd.stop()
			return True
		else:
			return False

pass  # RunCmdTimeout
