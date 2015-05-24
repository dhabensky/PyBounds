__author__ = 'admin'


shell_symbols = "\\'`\")(><$,|&*+;?]["


def escape_symbols(s, chars):
	for char in chars:
		s = s.replace(char, "\\" + char)
	return s
pass


def unescape_symbols(s, chars):
	for char in chars:
		s = s.replace("\\" + char, char)
	return s
pass


def shell_escape(s):
	return "'" + s.replace("'", "'\\''") + "'"
pass


def shell_unescape(s):
	return s[1:-1].replace("'\\''", "'")
pass