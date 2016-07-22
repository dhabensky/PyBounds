#!/usr/bin/python3.5

__author__ = 'admin'

import getopt
import sys
import TaskExecutor
from shutil import rmtree
from tempfile import mkdtemp
from External.TaskParser import TaskParser
from Shared.Files import *


def usage():
    print()
    print("USAGE:")
    print()
    print("  -h | --help                          - prints this message")
    print()
    print(" [-v | -s] [-t secs] [-m kilobytes] task_file")
    print("                                       - run task from 'task_file'")
    print("                                          in normal, (v)erbose or (s)ilent mode")
    print("                                          with optional time and/or memory limit")
    print()
    print("  -r | --reg module cls1 [ cls2 [...]] - register argument classes 'cls1'")
    print("                                          'cls2', ... from module 'module'")
    print()
    print("  -u | --unreg cls1 [ cls2 [...] ]     - unregister argument classes 'cls1'")
    print("                                          'cls2', ... ")
    print()
    print("  -p | --print                         - show registered classes")
    print()
    print("  -c | --clear                         - clear registered classes")
    print()
pass

verbose = False
silent = False

def main():

    global verbose
    global silent
    smart = False
    arch = "x86"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "vst:m:h:r:upc", ["help", "register=", "unregister", "print", "clear", "smart="])
    except getopt.GetoptError as err:
        print("    " + str(err))
        usage()
        sys.exit(2)
    pass

    # if not os.path.exists(os.path.expanduser("~/.PyBounds")):
    # 	os.mkdir(os.path.expanduser("~/.PyBounds"))

    dir_temp= mkdtemp()

    files = Files(dir_temp, '')
    if not os.path.exists(files.regclasses):
        try:
            open(files.regclasses, 'w').close()
        except:
            pass

    if len(sys.argv) == 1:
        usage()
        sys.exit()

    time = 1.5        # sec
    memory = 1000000  # Kb

    for o, a in opts:

        if o in ("-h", "--help"):
            usage()
            sys.exit()

        elif o == "--smart":
            arch = a
            smart = True

        elif o == "-v":
            if silent:
                print("    silent and verbose are exclusive options")
                usage()
                sys.exit(1)
            verbose = True

        elif o == "-s":
            if verbose:
                print("    silent and verbose are exclusive options")
                usage()
                sys.exit(1)
            silent = True

        elif o == "-t":
            try:
                time = float(a)
            except:
                print("    time must be a number")
                usage()
                exit(1)

            if time < 0:
                print("    time must be positive")
                usage()
                exit(1)

            if time < 1.5:
                print("    recommended time limit: > 1.5 seconds")

        elif o == "-m":
            try:
                memory = int(a)
            except:
                print("    memory must be a number")
                usage()
                exit(1)

            if memory < 0:
                print("    memory must be positive")
                usage()
                exit(1)

            if memory < 100000:
                print("    recommended memory limit: > 100000 Kb")

        elif o in ("-r", "--register"):
            module = a
            classes = args
            parser = TaskParser()
            parser.load_registered_classes(files.regclasses, silent=True)
            #print "registering classes " + " ".join(classes) + " in module " + module
            parser.register_by_query(module + " " + " ".join(classes), silent=False)
            parser.save_registered_classes(files.regclasses)
            sys.exit()

        elif o in ("-u", "--unregister"):
            classes = args
            parser = TaskParser()
            parser.load_registered_classes(files.regclasses, silent=True)
            #print "unregistering classes" + " ".join(classes) + " in module " + module
            parser.unregister_by_query(" ".join(classes), silent=False)
            parser.save_registered_classes(files.regclasses)
            sys.exit()

        elif o in ("-p", "--print"):
            os.system("cat " + files.regclasses + " 2>/dev/null")
            sys.exit()

        elif o in ("-c", "--clear"):
            os.system("rm " + files.regclasses + " 2>/dev/null")
            sys.exit()

        else:
            pass

    pass

    if len(args) > 0:
        TaskExecutor.main(dir_temp, args[0], time, memory, verbose, silent, smart, arch)
        rmtree(dir_temp)
    else:
        print("    required task_file")
        usage()
        exit(1)

pass

if __name__ == "__main__":
    main()
