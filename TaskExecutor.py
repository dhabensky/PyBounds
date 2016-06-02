#!/usr/bin/python2.7

__author__ = 'avdoshintheannihilator'

from os.path import dirname, realpath
from subprocess import *

from External.TaskParser import TaskParser
from External.ArgumentSequence import *
from External.TimeoutOutputParser import Parser
from External.RunCmdTimeout import RunCmdTimeout
from External.Escape import *
from Shared.ExecutionResult import ExecutionResult
from Shared.Files import *


realpath = str(dirname(realpath(__file__)))
files = Files('')


class TaskExecutor:

	def __init__(self):
		self.time_limit = 1.5          # sec
		self.memory_limit = 1000000    # Kb
		self.task_temp_file = None
		self.task_parser = None
	pass

	def run(self, verbose=False, silent=False):

		task_result = []
		task_list = self.task_parser.build_task_list(silent)
		for task in task_list:

			cases = []
			task_result.append(cases)
			oldresult = None
			progname = ""

			try:
				for current_args in task:

					if current_args[0].startswith("."):
						current_args[0] = os.path.abspath(current_args[0])
					progname = os.path.split(current_args[0])[1]

					current_args = " ".join(map(shell_escape, current_args))

					if verbose:
						print current_args

					# f = open(self.task_temp_file, 'w')
					# f.write(current_args)
					# f.close()

					result = self.exec_and_get_result(progname, current_args)

					if oldresult is None or not result.equal(oldresult):
						result.args_start_bound = current_args
						result.args_start_list = task.get_args_str()
						result.args_end_bound = current_args
						result.args_end_list = result.args_start_list
						cases.append(result)
					else:
						cases[len(cases) - 1].args_end_bound = current_args
						cases[len(cases) - 1].args_end_list = task.get_args_str()

					oldresult = result
				pass
			except Exception, ex:
				if not silent:
					print "Error during task " + progname
					print str(type(ex)) + " " + str(ex)
					print "Task not completed"
			pass

		pass

		dump(task_result, files.output)
		pass
	pass

	def res_from_dump(self):
		try:
			result = load(files.result_dump)
			result.log.append("OUT. deserialized from file")
			return result
		except:
			return ExecutionResult()
	pass

	def res_from_stderr(self):
		try:
			parser = Parser(self.time_limit, self.memory_limit)
			result = parser.parse_file(files.stderr)
			return result
		except:
			return ExecutionResult()
	pass

	def exec_and_get_result(self, progname, args):

		rm_file(files.result_dump)

		try:
			timeout = self.exec_gdb_timeout(progname, args)

		except Exception, ex:
			print str(ex.__class__.__name__) + " in exec_gdb(): " + str(ex)
			raise
		pass

		dumpres = self.res_from_dump()
		stderrres = self.res_from_stderr()

		if stderrres.state == 'memexceed':
			return stderrres

		if dumpres.state == 'crash':
			if timeout:
				res = ExecutionResult()
				res.on_timeout(self.time_limit)
				return res

			if stderrres.state == 'signal':
				return stderrres

			return dumpres

		if dumpres.state == 'exit' or dumpres.state == 'gdberror':
			return dumpres

		if timeout or stderrres.state == 'timeout':
			res = ExecutionResult()
			res.on_timeout(self.time_limit)
			return res

		if stderrres.state == 'signal':
			return stderrres

		return stderrres
	pass

	def exec_gdb_timeout(self, progname, args):
		try:
			echoarg = "python "\
					+ "path=\"" + str(realpath) + "\";"\
					+ "taskfile=\"" + self.task_parser.task_file + "\";"\
					+ "task=r\"" + args.replace('"', '\\"') + "\";"\
					+ "exec(open(\"" + str(realpath) + "/GdbInternal/Executor.py\").read())"
			# print echoarg
			# input()
			pipe = " | "
			gdbstart = "perl -w " + str(realpath) + "/timeout" + " -t " + str(self.time_limit) + " -m " + str(self.memory_limit)\
					+ " gdb --silent 2>" + shell_escape(files.stderr) + " 1>/dev/null"

			cmd = "echo " + shell_escape(echoarg) + pipe + gdbstart
			#print "cmd:", cmd
			return RunCmdTimeout(cmd, progname, self.time_limit).run()
		except Exception, ex:
			print ex
			return False
	pass

pass


def main(task_file, time, memory, verbose, silent):
	global files
	files = Files(task_file)

	if not os.path.exists(os.path.expanduser("~/.PyBounds")):
		os.mkdir(os.path.expanduser("~/.PyBounds"))

	try:
		files = Files(task_file)

		if not os.path.exists(files.regclasses):
			try:
				open(files.regclasses, 'w').close()
			except:
				pass

		parser = TaskParser()
		parser.set_task_file(files.task)
		parser.load_registered_classes(files.regclasses)

		executor = TaskExecutor()
		executor.task_parser = parser
		executor.task_temp_file = files.task_temp
		executor.time_limit = time
		executor.memory_limit = memory
		executor.run(verbose, silent)

		rm_file(files.result_dump)
		rm_file(files.task_temp)
		#os.system("cat " + shell_escape(files.stderr))
		rm_file(files.stderr)

	except Exception, ex:
		print str(ex)

	print "PyBounds: tasks completed"
pass
