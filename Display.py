#!/usr/bin/python3.5

import pickle
import sys

def main():
	if len(sys.argv) == 1:
		print("file argument required")
		exit(1)

	try:
		f = open(sys.argv[1], 'rb')
		task_result = pickle.load(f)
		f.close()
	except Exception as ex:
		print("cannot open file: " + sys.argv[1] + " " + str(ex))
		exit(1)

	print("")


	for i in range(0, len(task_result)):

		if len(task_result[i]) != 0:
			progname = task_result[i][0].args_start_list[0]
		else:
			print("\n = #" + str(i) + ": no data ==========")
			continue

		print("\n = #" + str(i) + " " + progname + " ==========")
		for case in task_result[i]:
			print(case)
			print("  from: " + ", ".join(case.args_start_list[1:]))
			print("    to: " + ", ".join(case.args_end_list[1:]))
		pass
	pass

if __name__ == "__main__":
	main()