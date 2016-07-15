__author__ = 'admin'

import os


class SimpleArg:

	def __init__(self, s):
		self.raw_string = str(s)
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


class LetterArg:

	def __init__(self):
		self.cur_letter = ord('A') - 1
	pass

	def __next__(self):
		if self.cur_letter < ord('z'):
			if self.cur_letter == ord('Z'):
				self.cur_letter = ord('a')
			else:
				self.cur_letter += 1
			return "-" + chr(self.cur_letter)
		else:
			raise StopIteration()
	pass

	def __str__(self):
		return "-" + chr(self.cur_letter)
	pass

	def __iter__(self):
		self.cur_letter = ord('A') - 1
		return self
	pass

pass


class ListArg:

	def __init__(self, l):
		self.ind = -1
		self.list = l
		if len(self.list) == 0:
			raise Exception("list must not be empty")

	pass

	def __next__(self):
		if self.ind < len(self.list) - 1:
			self.ind += 1
			return self.list[self.ind]
		else:
			raise StopIteration()
	pass

	def __str__(self):
		return self.list[self.ind]
	pass

	def __iter__(self):
		self.ind = -1
		return self
	pass

pass


class LongArgFromFile:

	def __init__(self, filename, start, end, step=1):

		if start < 0 or end < 0:
			raise Exception("LongArgFromFile: start and end must be > 0")
		if step == 0:
			raise Exception("LongArgFromFile: step must not be 0")

		self.start = start
		self.end = end
		self.step = step
		self.file = os.path.expanduser(filename)
		self.current_count = self.start - self.step

		try:
			f = open(self.file, 'r')
			self.content = f.readline()
			if self.end > len(self.content):
				self.end = len(self.content) + 1
			if self.start > len(self.content):
				self.start = len(self.content)
			f.close()
		except:
			raise Exception("LongArgFromFile: cannot open file " + filename)

		if not self.has_next():
			raise Exception("LongArgFromFile: incorrect range. "
					+ "start=" + str(self.start) + ", end=" + str(self.end) + ", step=" + str(self.step))
	pass

	def __next__(self):
		if self.has_next():
			self.current_count += self.step
			return self.content[:self.current_count]
		else:
			raise StopIteration()
	pass

	def has_next(self):
		if self.step > 0:
			return self.current_count + self.step < self.end
		else:
			return self.current_count + self.step > self.end
	pass

	def __str__(self):
		return "length=" + str(self.current_count)
	pass

	def __iter__(self):
		self.current_count = self.start - self.step
		return self
	pass

pass