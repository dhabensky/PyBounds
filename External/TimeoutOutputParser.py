from Shared.ExecutionResult import ExecutionResult

__author__ = 'avdoshintheannihilator'


class Parser:

	def __init__(self, time_limit, memory_limit):
		self.cause = ''
		self.cpu = 0
		self.mem = 0
		self.maxmem = 0
		self.stale = 0
		self.time_limit = time_limit
		self.memory_limit = memory_limit
	pass

	def is_timeout_output(self, s):
		words = s.split(' ')
		success = False

		if len(words) == 9 and words[1] == "CPU" and words[3] == "MEM":
			if words[5] == "MAXMEM" and words[7] == "STALE":
				self.cause = words[0]
				self.cpu = words[2]
				self.mem = words[4]
				self.maxmem = words[6]
				self.stale = words[8]
				success = True
		return success
	pass

	def parse_file(self, filename):

		result = ExecutionResult()
		result.log.append("OUT. parsing file")

		f = open(filename, 'r')
		lines = f.readlines()
		f.close()

		for l in lines:
			if self.is_timeout_output(l):
				if self.cause == "TIMEOUT":
					result.on_timeout(self.time_limit)
					result.log.append("OUT. timeout")
				elif self.cause == "MEM":
					result.on_exceed_memlimit(self.memory_limit)
					result.log.append("OUT. memory")
				elif self.cause == "SIGNAL":
					result.on_signal()
					result.log.append("OUT. signal")
				elif self.cause == "FINISHED":
					result.state = 'finished'
					result.log.append("OUT. finished")
					pass
				pass
				break
			pass
		pass

		if result.state == 'raw':
			result.log("OUT. timeout log not found")

		return result
	pass

pass
