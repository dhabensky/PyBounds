#!/usr/bin/python3.5

__author__ = 'avdoshintheannihilator'

import struct

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
#files = Files('')


class TaskExecutor:

    def __init__(self):
        self.time_limit = 1.5          # sec
        self.memory_limit = 1000000    # Kb
        self.task_temp_file = None
        self.task_parser = None

        # smart mode
        self.str_param = None
        self.ip_coincidence = None
        self.args_max = None
        self.end_bounds_check = False
        self.arch = None

    def check_ip(self, ip, curent_args):
        adr = str(ip)
        # print(adr)
        position = adr.find('x')
        adr = adr[(position + 1):]
        # print("target = " + target)
        adr = int(adr, 16)
        try:
            str_adr = ((struct.pack(">I", adr)).decode())[::-1]
            # print (str_adr)
        except:
            return False
        if self.arch == "x86":
            if (len(str_adr) == 4) and (self.str_param.find(str_adr) != -1):
                if self.ip_coincidence is None:
                    self.ip_coincidence = str_adr
                    curent_args = curent_args.replace('\t', ' ')
                    print(curent_args)
                    return False
                if self.ip_coincidence != str_adr:
                    print(self.args_max)
                    return True
                else:
                    curent_args = curent_args.replace('\t', ' ')
                    self.args_max = curent_args
                    return False

            elif self.ip_coincidence is not None:
                print(self.args_max)
                return True
        elif self.arch == "x64":
            if ((len(str_adr) >= 4) or (len(str_adr) <= 6)) and (self.str_param.find(str_adr) != -1):
                if self.ip_coincidence is None:
                    self.ip_coincidence = str_adr
                    curent_args = curent_args.replace('\t', ' ')
                    print(curent_args)
                    return False
                if self.ip_coincidence != str_adr:
                    print(self.args_max)
                    return True
                else:
                    curent_args = curent_args.replace('\t', ' ')
                    self.args_max = curent_args
                    return False

            elif self.ip_coincidence is not None:
                print(self.args_max)
                return True



    def run(self, verbose=False, silent=False, smart=False):

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

                    current_args = "\t".join(map(shell_escape, current_args))
                    # print(current_args)

                    if verbose:
                        print(current_args)

                    result = self.exec_and_get_result(progname, current_args)

                    if smart:
                        if result.ip != 0:
                            if self.check_ip(result.ip, current_args):
                                self.end_bounds_check = True
                                break

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
            except Exception as ex:
                if not silent:
                    print("Error during task " + progname)
                    print(str(type(ex)) + " " + str(ex))
                    print("Task not completed")
        if not self.end_bounds_check and smart:
            print(self.args_max)
        dump(task_result, files.output)

    def res_from_dump(self):
        try:
            result = load(files.result_dump)
            result.log.append("OUT. deserialized from file")
            return result
        except:
            return ExecutionResult()

    def res_from_stderr(self):
        try:
            parser = Parser(self.time_limit, self.memory_limit)
            result = parser.parse_file(files.stderr)
            return result
        except:
            return ExecutionResult()

    def exec_and_get_result(self, progname, args):

        rm_file(files.result_dump)

        try:
            timeout = self.exec_gdb_timeout(progname, args)

        except Exception as ex:
            print(str(ex.__class__.__name__) + " in exec_gdb(): " + str(ex))
            raise

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

    def exec_gdb_timeout(self, progname, args):
        try:

            # + "task=r\"" + args.replace('"', '\\"') + "\";"\

            echoarg = "python "\
                    + "path=\"" + str(realpath) + "\";"\
                    + "dir_name=\"" + self.task_parser.dir_name + "\";"\
                    + "taskfile=\"" + self.task_parser.task_file + "\";"\
                    + "exec(open(\"" + str(realpath) + "/GdbInternal/Executor.py\").read())"
            # print echoarg
            # input()
            # print()
            task_to_gdb = open((self.task_parser.dir_name + "/task_to_gdb"), 'w')
            task_to_gdb.write(args)
            task_to_gdb.close()

            pipe = " | "
            gdbstart = "perl -w " + str(realpath) + "/timeout" + " -t " + str(self.time_limit) + " -m " + str(self.memory_limit)\
                    + " gdb --silent 2>" + shell_escape(files.stderr) + " 1>/dev/null"

            cmd = "echo " + shell_escape(echoarg) + pipe + gdbstart
            # print("cmd :", cmd)
            # print()

            return RunCmdTimeout(cmd, progname, self.time_limit).run()
        except Exception as ex:
            print("exec_gdb_timeout " + str(ex))
            return False



def main(dir_name, task_file, time, memory, verbose, silent, smart, arch):
    global files
    # print(realpath)
    files = Files(dir_name, task_file)

    # if not os.path.exists(os.path.expanduser("~/.PyBounds")):
    # 	os.mkdir(os.path.expanduser("~/.PyBounds"))

    try:
        files = Files(dir_name, task_file)

        if not os.path.exists(files.regclasses):
            try:
                open(files.regclasses, 'w').close()
            except:
                pass

        parser = TaskParser()
        executor = TaskExecutor()

        # executor.compression = CompressionParameters()
        # executor.compression.main(files.task)

        parser.dir_name = dir_name
        parser.set_task_file(files.task)
        parser.load_registered_classes(files.regclasses)

        # executor.compression.return_file_back(files.task)

        executor.task_parser = parser
        executor.task_temp_file = files.task_temp
        executor.time_limit = time
        executor.memory_limit = memory

        if smart:
            file_param = open(task_file, 'r')
            executor.str_param = str(file_param.read())
            file_param.close()

            position = executor.str_param.find("LongArgFromFile(\'")
            executor.str_param = executor.str_param[position + 17:]
            position = executor.str_param.find("\'")
            executor.str_param = executor.str_param[:position]

            file_param = open(executor.str_param, 'r')
            executor.str_param = str(file_param.read())
            file_param.close()

            executor.arch = arch

        executor.run(verbose, silent, smart)


        rm_file(files.result_dump)
        rm_file(files.task_temp)
        #os.system("cat " + shell_escape(files.stderr))
        rm_file(files.stderr)

    except Exception as ex:
        print("TaskExecutor.main error" + str(ex))

    if not smart:
        print("PyBounds: tasks completed")
