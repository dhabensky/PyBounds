__author__ = 'avdoshintheannihilator'


class ExecutionResult:

	def __init__(self):
		self.state = 'raw'
		self.exit_code = 0
		self.signo = 0
		self.ip = 0
		self.gdb_error = ""
		self.timelimit = 0
		self.memlimit = 0
		self.args_start_bound = ""
		self.args_end_bound = ""
		self.args_start_list = []
		self.args_end_list = []
		self.log = []
	pass

	def on_exit(self, code):
		self.exit_code = code
		self.state = 'exit'
	pass

	def on_crash(self, signo, ip):
		self.signo = signo
		self.ip = ip
		self.state = 'crash'
	pass

	def on_gdb_error(self, s):
		self.gdb_error = s
		self.state = 'gdberror'
	pass

	def on_timeout(self, time):
		self.timelimit = time
		self.state = 'timeout'
	pass

	def on_exceed_memlimit(self, memlimit):
		self.memlimit = memlimit
		self.state = 'memexceed'
	pass

	def on_signal(self):
		self.state = 'signal'
	pass

	def equal(self, other):
		if self.state == other.state:
			if self.state == 'exit':
				return self.exit_code == other.exit_code
			if self.state == 'crash':
				return self.signo == other.signo and self.ip == other.ip
			if self.state == 'gdberror':
				return self.gdb_error == other.gdb_error
			if self.state == 'timeout':
				return self.timelimit == other.timelimit
			if self.state == 'memexceed':
				return self.memlimit == other.memlimit
			if self.state == 'signal':
				return True
			else:
				return True
		pass
	pass

	def __str__(self):
		if self.state == 'exit':
			return 'exit. code=' + str(self.exit_code)
		if self.state == 'crash':
			return 'crash. signal=' + str(self.signo) + ", ip=" + str(self.ip)
		if self.state == 'gdberror':
			return 'gdb_error. ' + self.gdb_error
		if self.state == 'timeout':
			return 'timeout. time limit=' + str(self.timelimit) + "sec"
		if self.state == 'memexceed':
			return 'memory. memory limit=' + str(self.memlimit) + "Kb"
		if self.state == 'signal':
			return 'signal. terminated by signal'
		else:
			return ' - invalid state: ' + str(self.state)
	pass

pass
