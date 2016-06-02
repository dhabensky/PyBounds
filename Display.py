#!/usr/bin/python2.7

import pickle
from Shared.Files import Files
from External.Escape import *
import sys

if len(sys.argv) == 1:
	print "file argument required"
	exit(1)

try:
	f = open(sys.argv[1], 'r')
	p = pickle.Unpickler(f)
	task_result = p.load()
	f.close()
except:
	print "cannot open file: " + sys.argv[1]
	exit(1)


print ""


for i in xrange(0, len(task_result)):

	if len(task_result[i]) != 0:
		progname = task_result[i][0].args_start_list[0]
	else:
		print "\n = #" + str(i) + ": no data =========="
		continue

	print "\n = #" + str(i) + " " + progname + " =========="
	for case in task_result[i]:
		print case
		print "  from: " + ", ".join(case.args_start_list[1:])
		print "    to: " + ", ".join(case.args_end_list[1:])
	pass
pass
