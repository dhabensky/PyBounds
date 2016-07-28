#!/usr/bin/python3.5


import sys
import struct
from shutil import rmtree
import pickle
import subprocess
from tempfile import mkdtemp



def usage():
    print()
    print("Example:")
    print("./CompressionParameters.py /home/max/C++Prog/ierror/ierror --arch=x86 ADASKJDJHGHJGHJGHJGJKSHDJ fhjkdsfh 3456378hj")
    print()


def main():

    # if not os.path.exists(os.path.expanduser("~/.ComPam")):
    # 	os.mkdir(os.path.expanduser("~/.ComPam"))

    dir_temp = mkdtemp()

    param = []
    arch = "x86"
    smart = False

    if len(sys.argv) < 3:
        usage()
        sys.exit(2)

    target = sys.argv[1]
    for a in sys.argv[2:]:
        if a.find("--arch=") != -1:
            arch = a[len("--arch="):]
        elif a.find("--smart") != -1:
            smart = True
        else:
            param.append(a)

    mparam = param[0]
    mparam_size = len(mparam)
    mparam_number = 0
    count = 1
    for par in param[1:]:
        if len(par) > mparam_size:
            mparam_size = len(par)
            mparam = par
            mparam_number = count
        count += 1

    param[mparam_number] = "\n"

    x86 = True

    if arch == "x64":
        x86 = False
    elif arch == "x86":
        x86 = True

    # Create A file
    f = open(dir_temp + "/A", 'w')
    f.write(mparam)
    f.close()

    # Create Task file
    task_filename = dir_temp + "/file"
    f = open(task_filename, 'w')
    f.write("\"" + target + "\"" + ", ")
    len_param = len(param)
    count = 1
    for par in param:
        if par == "\n":
            f.write("LongArgFromFile('" + dir_temp + "/A" + "'")
            f.write(", " + str(1) + ", " + str(len(mparam) + 1))
        else:
            f.write("SimpleArg(\"" + par + "\"")
        if count != len_param:
            f.write("), ")
        else:
            f.write(")")
        count += 1

    f.close()
    # RUN PyBounds

    if smart:
        p = subprocess.Popen(["./PyBounds.py", "--smart=" + str(arch), task_filename])
        p.wait()
    else:
        p = subprocess.Popen(["./PyBounds.py", task_filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.wait()

        # Display
        try:
            f = open(task_filename + '_output', 'rb')
            task_result = pickle.load(f)
            f.close()
        except:
            print("cannot open file: " + sys.argv[1])
            exit(1)

        print("")

        for i in range(0, len(task_result)):

            # if len(task_result[i]) != 0:
            # 	progname = task_result[i][0].args_start_list[0]
            # else:
            # 	print("\n = #" + str(i) + ": no data ==========")
            # 	continue

            if len(task_result[i]) == 0:
                print("\n = #" + str(i) + ": no data ==========")
                continue

            for case in task_result[i]:
                # print(case)
                adr = str(case)
                position = adr.find("ip=")
                if position != -1:
                    adr = adr[(position + 3):]
                    # print("target = " + target)
                    adr = int(adr, 16)
                    try:
                        str_adr = ((struct.pack(">I", adr)).decode())[::-1]
                        # print (str_adr)
                    except:
                        continue
                    if x86:
                        if (len(str_adr) == 4) and (mparam.find(str_adr) != -1):
                            # print(True)
                            for ar in case.args_start_list[1:]:
                                length = str(ar)
                                # print(target)
                                if length.find("length=") != -1:
                                    length = length[7:]
                                    param[mparam_number] = mparam[:int(length)]
                                    print(target + ' ' + " ".join(param))
                    else:
                        if ((len(str_adr) >= 4) or (len(str_adr) <= 6)) and (mparam.find(str_adr) != -1):
                            # print(True)
                            for ar in case.args_start_list[1:]:
                                length = str(ar)
                                # print(target)
                                if length.find("length=") != -1:
                                    length = length[7:]
                                    print("CompressionParametrMutable = " + mparam[:int(length)] + " size = " + length)
                else:
                    continue
                pass
        pass
    rmtree(dir_temp)

if __name__ == "__main__":
    main()
