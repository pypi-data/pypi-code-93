def print(*w,times=0,endl="\n",sepr=" "):
    import time,sys
    for i in str(w):
        for j in str(i):
            sys.stdout.write(j)
            time.sleep(float(times))
        if w.index(i)!=len(w)-1:
            sys.stdout.write(sepr)
    sys.stdout.write(endl)
def clean():
    import sys
    sys.stdout.write("\033[2J\033[00H")
def logo(color):
    color=str(color)
    for i in color:
        if i=="0":
            print("\033[40m ",endl="")
        elif i=="1":
            print("\033[41m ",endl="")
        elif i=="2":
            print("\033[42m ",endl="")
        elif i=="3":
            print("\033[43m ",endl="")
        elif i=="4":
            print("\033[44m ",endl="")
        if i=="5":
            print("\033[45m ",endl="")
        elif i=="6":
            print("\033[46m ",endl="")
        elif i=="7":
            print("\033[47m ",endl="")
        elif i=="k":
            print("\033[30m",endl="")
        elif i=="r":
            print("\033[31m",endl="")
        elif i=="g":
            print("\033[32m",endl="")
        elif i=="y":
            print("\033[33m",endl="")
        elif i=="b":
            print("\033[34m",endl="")
        elif i=="m":
            print("\033[35m",endl="")
        elif i=="c":
            print("\033[36m",endl="")
        elif i=="w":
            print("\033[37m",endl="")
        else:
            print(i,endl="")