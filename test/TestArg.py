__author__ = 'admin'


class TestArg:

	def __init__(self):
		self.raw_string = 'TestArg'
		self.used = False
	pass

	def __next__(self):
		if not self.used:
			self.used = True
			return self.raw_string
		else:
			raise StopIteration()
	pass

	def __str__(self):
		return self.raw_string
	pass

	def __iter__(self):
		self.used = False
		return self
	pass

pass

