__author__ = 'admin'

import os
import pickle
from External.Escape import *


class Files(object):

	def __init__(self, dir_temp, task_file):
		filename = task_file[(task_file.rfind('/')):]
		self.dir_name = dir_temp
		self.task = task_file
		self.task_temp = os.path.expanduser(dir_temp + filename + '_current')
		self.stderr = os.path.expanduser(dir_temp + filename + '_stderr')
		self.result_dump = os.path.expanduser(dir_temp+ filename + '_resultdump')
		self.output = os.path.expanduser(task_file + '_output')
		self.regclasses = os.path.expanduser(dir_temp + '/registered_classes')
		Files.regclasses = self.regclasses
	pass

pass


def rm_file(s):
	try:
		os.system('fuser -k \'' + shell_esc(s) + "\' 2> /dev/null")
		os.system("rm \'" + shell_esc(s) + "\' 2> /dev/null")
	except:
		pass
pass


def dump(obj, filename):
	try:
		f = open(filename, 'wb')
		pickle.dump(obj, f, protocol=0)
		f.close()
	except Exception as ex:
		print("trouble while dumping: " + str(ex.__class__.__name__) + " " + str(ex))
		raise
pass


def load(filename):
	try:
		f = open(filename, 'rb')
		obj = pickle.load(f)
		f.close()
		return obj
	except Exception as ex:
		print("trouble while loading: " + str(ex.__class__.__name__) + " " + str(ex))
		raise
pass
