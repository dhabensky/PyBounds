__author__ = 'avdoshintheannihilator'

import sys
sys.path.append(path)

from Shared.Files import *
files = Files(dir_name, taskfile)

from GdbInternal import gdb_utils
from Shared.ExecutionResult import ExecutionResult


def debug_print(s, name_log):
	directory = "/home/fuzzer/"
	directory += name_log
	format_file = ".txt"
	directory += format_file

	ffff = open(directory, 'a')
	ffff.write(s)
	ffff.write('\n')
	ffff.close()


class Executor:

	def __init__(self):
		self.result = ExecutionResult()
		self.info = ""
		self.set_handlers()
	pass

	def run(self, s):

		split = s.find("\t")
		s = s.replace("\t", " ")
		try:
			if split == -1:
				gdb.execute("file " + s)
				gdb.execute("run")
			else:
				gdb.execute("file " + s[:split])
				gdb.execute("run " + s[split + 1:])
			pass
		except gdb.error as ex:
			self.result.on_gdb_error(str(ex))
			print(ex)
		except Exception as ex:
			self.result.log.append(str(ex))

		return self.result
	pass

	@staticmethod
	def get_info(signo):
		try:
			s = gdb_utils.execute_output("info signal " + str(signo))[1]
			pref = s[:s.find(' ')] + ", "
			s = s[s.rfind('\t'):]
			for i in range(len(s)):
				if not s[i].isspace():
					s = s[i:]
					break
			return pref + s
		except:
			return ""
	pass

	def set_handlers(self):

		try:
			def get_ip():
				ip = gdb.parse_and_eval("$ip")
				if str(ip.type) == "void":
					ip = gdb.parse_and_eval("$eip")
				if str(ip.type) == "void":
					ip = gdb.parse_and_eval("$rip")

				ip = str(ip)
				if ip.find(" ") != -1:
					ip = ip[:ip.find(" ")]
				return ip
			pass

			def exit_handler(event):
				if hasattr(event, 'exit_code'):
					self.result.on_exit(event.exit_code)
				self.result.log.append("IN. exiting gdb")
			pass
			gdb.events.exited.connect(exit_handler)

			def stop_handler(event):
				signo = str(gdb.parse_and_eval("$_siginfo.si_signo"))
				self.info = signo + " (" + self.get_info(signo) + ")"
				self.result.on_crash(self.info, get_ip())
				self.result.log.append("IN. stop on signal")
			pass
			gdb.events.stop.connect(stop_handler)

		except Exception as ex:
			print("exception in set_handlers(): " + str(ex))
		pass
	pass

pass


def main():
	try:
		# debug_print(dirname, "check")
		f = open((dir_name + "/task_to_gdb"), 'r')
		task = str(f.read())
		f.close()

		print(task)


		executor = Executor()
		executor.run(task)
		dump(executor.result, files.result_dump)

	except IOError as ex:
		print(str(ex))
		#debug_print(str(ex), "error")
	pass
pass


main()
