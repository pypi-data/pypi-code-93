def print(*w,times=0,endl="\n",sepr=" "):
    import time,sys
    for i in w:
        for j in i:
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
            print("\033[40m ")
        elif i=="1":
            print("\033[41m ")
        elif i=="2":
            print("\033[42m ")
        elif i=="3":
            print("\033[43m ")
        elif i=="4":
            print("\033[44m ")
        if i=="5":
            print("\033[45m ")
        elif i=="6":
            print("\033[46m ")
        elif i=="7":
            print("\033[47m ")
        elif i=="k":
            print("\033[30m")
        elif i=="r":
            print("\033[31m")
        elif i=="g":
            print("\033[32m")
        elif i=="y":
            print("\033[33m")
        elif i=="b":
            print("\033[34m")
        elif i=="m":
            print("\033[35m")
        elif i=="c":
            print("\033[36m")
        elif i=="w":
            print("\033[37m")