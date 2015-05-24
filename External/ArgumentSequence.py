__author__ = 'avdoshintheannihilator'


class ArgumentSequence:

	def __init__(self, args):
		self.args = args
		self.iters = []
		self.state = []

		ind = 0

		try:
			for i, arg in enumerate(self.args):
				ind = i
				self.iters.append(iter(arg))
		except:
			raise Exception("argument " + str(ind) + " (class=" + str(self.args[ind].__class__.__name__) + ") is not iterable")

		try:
			for i, it in enumerate(self.iters):
				ind = i
				self.state.append(it.next())
			self.iters[len(self.args) - 1] = iter(self.args[-1])
		except:
			raise Exception("argument " + str(ind) + " (class=" + str(self.args[ind].__class__.__name__) + ") has no values")

		self.current_arg = len(self.args) - 1
	pass

	def next(self):
		try:

			while True:
				try:
					self.state[self.current_arg] = self.iters[self.current_arg].next()

					for i in xrange(self.current_arg + 1, len(self.args)):
						self.iters[i] = iter(self.args[i])
						self.state[i] = self.iters[i].next()

					self.current_arg = len(self.args) - 1
					return self.state

				except StopIteration:
					self.current_arg -= 1
					if self.current_arg < 0:
						raise StopIteration()
			pass
		except StopIteration:
			raise
		except Exception, ex:
			print str(type(ex)) + " " + str(ex)
	pass

	def get_args_str(self):
		return [str(arg) for arg in self.args]
	pass

	def __iter__(self):
		return self
	pass

pass
