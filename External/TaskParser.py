__author__ = 'admin'

from External.ArgumentSequence import *
from External.Import import Import
from ArgClasses.BuiltInArgs import *


def printable(s):
	for ch in s:
		if " \t\n\r".find(ch) == -1:
			return True
	return False
pass


class TaskParser:

	def __init__(self):
		self.registered_classes = {}
		self.asterisk_import = []
		self.register_by_query("BuiltInArgs *", silent=True)
		self.task_file = None
		self.__lines__ = None
	pass

	def set_task_file(self, task_file):
		try:
			f = open(task_file, 'r')
			self.__lines__ = f.readlines()
			f.close()
			self.task_file = task_file
		except:
			raise IOError('cannot open file ' + task_file)
	pass

	def build_task_list(self, silent=False):

		task_list = []
		for line in self.__lines__:

			line = line.strip()
			if line.startswith("#") or not printable(line):
				continue

			try:
				task_list.append(self.__parse_line__(line))
			except Exception, ex:
				if not silent:
					print "Error parsing task:\n" + line
					print ex
			pass
		pass

		return task_list
	pass

	# def __parse_line__(self, s):
	# 	args = []
	# 	cur_ind = 0
	# 	space_ind = s.find(" ", cur_ind)
	# 	while space_ind != -1:
	# 		token = s[cur_ind:space_ind]
	# 		cls = self.__get_class__(token)
	# 		if cls is not None:
	# 			imp = "from " + cls.__module__ + " import " + cls.__name__
	# 			print imp
	# 			exec imp
	# 			print "exec finished"
	# 			back = s.find(")", cur_ind)
	# 			arg = s[s.find("(", cur_ind) + 1:back]
	# 			print "before eval. arg = " + arg
	# 			args.append(eval(cls.__name__ + '(' + arg + ')'))
	# 			print "before eval"
	# 			#args.append(cls(*arg.split(',')))  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<      SHIT
	# 			cur_ind = back + 2
	# 		else:
	# 			args.append(SimpleArg(token))
	# 			cur_ind = space_ind + 1
	# 		space_ind = s.find(" ", cur_ind)
	#
	# 	token = s[cur_ind:]
	# 	cls = self.__get_class__(token)
	# 	if cls is not None:
	# 		back = s.find(")", cur_ind)
	# 		arg = s[s.find("(", cur_ind) + 1:back]
	# 		args.append(eval(cls + "('" + arg + "')"))
	# 	else:
	# 		args.append(SimpleArg(token))
	#
	# 	return ArgumentSequence(args)
	# pass

	def __parse_line__(self, s):

		args = eval("[" + s + "]")

		for i in xrange(len(args)):
			if isinstance(args[i], str) or isinstance(args[i], int) or isinstance(args[i], float):
				args[i] = SimpleArg(args[i])
			elif isinstance(args[i], list) or isinstance(args[i], tuple):
				args[i] = ListArg(args[i])
			elif not hasattr(args[i], "__iter__"):
				raise Exception(args[i].__class__.__name__ + " is not iterable")

		return ArgumentSequence(args)
	pass

	def __register_arg_class__(self, classobj, module_name):
		existing = self.__find_registered_class__(classobj.__name__)
		if existing is None:
			self.registered_classes[classobj] = module_name
			globals()[classobj.__name__] = classobj
		elif existing[1] == module_name:
			raise Exception(existing[1] + "." + existing[0].__name__ + ": class already registered")
		else:
			raise Exception(module_name + "." + existing[0].__name__ + ": class conflicts with " + existing[1] + "." + existing[0].__name__)
	pass

	def __unregister_arg_class__(self, class_name):
		for cls, mod in self.registered_classes.iteritems():
			if cls.__name__ == class_name:
				try:
					self.registered_classes.pop(cls, None)
					self.asterisk_import.remove(mod)
					globals().pop(cls.__name__, None)
				except:
					pass
				return
		raise Exception(class_name + ": class not registered")
	pass

	def __find_registered_class__(self, classname):
		for cls, mod in self.registered_classes.iteritems():
			if cls.__name__ == classname:
				return cls, mod
		return None
	pass

	def __get_class__(self, token):
		for cls, mod in self.registered_classes.iteritems():
			if token.startswith(cls.__name__):
				return cls
		return None
	pass

	def load_registered_classes(self, filename, silent=True):
		try:
			f = open(filename, 'r')
			lines = f.readlines()
			f.close()

			# if not silent:
			# 	print "loading argument classes"

			for line in lines:
				self.register_by_query(line, silent)

			# if not silent:
			# 	print "done"

		except Exception, ex:
			if not silent:
				print 'error loading argument classes: ' + str(ex)
	pass

	def save_registered_classes(self, filename):

		v = {}
		for key, value in sorted(self.registered_classes.iteritems()):
			v.setdefault(value, []).append(key)

		for i in self.asterisk_import:
			if (v[i]) != 0:
				v[i] = ["*"]

		try:
			v.pop("ArgClasses.BuiltInArgs", None)
		except:
			pass

		try:
			f = open(filename, 'w')
			for mod, clss in v.iteritems():
				f.write(mod[mod.find('.') + 1:] + " " + " ".join(map(lambda c: c.__name__, clss)) + "\n")
			f.close()
		except:
			pass

	pass

	def register_by_query(self, query, silent=False):
		try:
			clss = Import.from_query(query, "ArgClasses")
			if not clss is None:

				if clss.all and clss.module not in self.asterisk_import:
					self.asterisk_import.append(clss.module)

				for cls in clss.classes:
					try:
						self.__register_arg_class__(cls, clss.module)
						if not silent:
							print "    + " + cls.__name__
					except Exception, ex:
						if not silent:
							print "    - " + str(ex)
					pass
				pass
			pass

		except Exception, ex:
			if not silent:
				print "    - error: " + str(ex)
	pass

	def unregister_by_query(self, query, silent=False):


		query = query.strip()
		if query.startswith('#') or not printable(query):
			return

		words = query.split(' ')
		words = filter(lambda w: w != '', words)
		# if len(words) == 1:
		# 	words.append(words[0][words[0].rfind('.') + 1:])

		for word in words:
			try:
				self.__unregister_arg_class__(word)
			except Exception, ex:
				if not silent:
					print "    - " + str(ex)
	pass

pass
