__author__ = 'admin'

import inspect


def printable(s):
	for ch in s:
		if " \t\n\r".find(ch) == -1:
			return True
	return False
pass


class Import:

	def __init__(self):
		self.module = ""
		self.classes = []
		self.all = False
	pass

	@staticmethod
	def from_query(query, package):
		if package != '' and not package.endswith('.'):
			package += '.'

		query = query.strip()
		if query.startswith('#') or not printable(query):
			return None

		words = query.split(' ')
		words = filter(lambda w: w != '', words)
		if len(words) == 1:
			words.append(words[0][words[0].rfind('.') + 1:])

		return Import.__import__(package + words[0], words[1:])
	pass

	@staticmethod
	def __import__(modname, classname_list):

		mod = __import__(modname)
		components = modname.split('.')
		for comp in components[1:]:
			mod = getattr(mod, comp)

		imp = Import()
		imp.module = modname

		if '*' in classname_list:
			imp.all = True
			for key, value in inspect.getmembers(mod, inspect.isclass):
				imp.classes.append(value)
		else:
			for cls in classname_list:
				try:
					imp.classes.append(getattr(mod, cls))
				except:
					print("    - " + mod.__name__ + "." + cls + ": class not found")

		return imp
	pass

pass