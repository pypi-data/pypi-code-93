from time import sleep
from random import uniform
import sys
from time import*
def clear():
    print("\033[2J")
    print("\033[999999999A",end="")
def jdt(time):
    loadList = ['?','?','?','?','?','?','?','?','?','?','?']
    for i in range(1,99+1):
        clear()
        print(loadList[i%11]+i//2*'\033[42m \033[0m'+(100//2-i//2)*'\033[47m \033[0m'+str(i)+'%')
        sleep(time)
    clear()
    print(loadList[101%11]+101//2*'\033[42m \033[0m'+(100//2-101//2)*'\033[47m \033[0m'+str(100)+'%')
    clear()
    print("加载完成!")
def prc(Text,timee):
    for i in Text:
        sleep(timee)
        print(i,end='',flush=True)
        sys.stdout.flush()
    print("", end="\n")
def title(text___):
    print("\033[38;2;100;200;200m\033[4m"+text___+"\033[0m")
def prtext(___text):
    print("\033[92m"+___text+"\033[0m")
def logo(a):
    for x in range(len(a)):
        if a[x]=="1":
            print("\033[41m ",end="")
        elif a[x]=="2":
            print("\033[42m ",end="")
        elif a[x]=="3":
            print("\033[43m ",end="")
        elif a[x]=="4":
            print("\033[44m ",end="")
        elif a[x]=="5":
            print("\033[45m ",end="")
        elif a[x]=="6":
            print("\033[46m ",end="")
        elif a[x]=="7":
            print("\033[47m ",end="")
        elif a[x]=="8":
            print("\033[48m ",end="")
        elif a[x]=="9":
            print("\033[49m ",end="")
        elif a[x]=="0":
            print("\033[40m ",end="")
        else:
            print(a[x],end="")
    print("\033[0m")
def css(a,yangshi):
    if yangshi=="card":
        h1 = "─"
        h2 = " "
        f = "!@#$%^&*()_+-=,.`\[]{};':<>|"
        list = [49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 183, 65]
        i = 1
        l = 65
        y = 0
        n = 0
        for i in range(57):
            if i == 26:
                l = 96
            l = l + 1
            list.append(l)
        for i in range(len(a)):
            i1 = i + 1
            a1 = a[i:i1]
            a1 = ord(a1)
            if a1 in list:
                y = y + 1
            else:
                n = n + 1
        if n == 0 and y > 0:
            k1 = "─"
            k2 = " "
        if n > 0 and y == 0:
            k1 = "─" * 2
            k2 = " " * 2
        else:
            k1 = "─"
            k2 = " "
        for i in range(len(a)):
            h1 = h1 + k1
            h2 = h2 + k2
        if n > 0 and y > 0:
            h1 = h1 + "─" * n
            h2 = h2 + "-" * n
        print("┌─" + h1 + "┐")
        print("│ " + a + " │")
        print("└─" + h1 + "┘")
    if yangshi=="logo":
        for x in range(len(a)):
            if a[x] == "1":
                print("\033[101m ", end="")
            elif a[x] == "2":
                print("\033[102m ", end="")
            elif a[x] == "3":
                print("\033[103m ", end="")
            elif a[x] == "4":
                print("\033[104m ", end="")
            elif a[x] == "5":
                print("\033[105m ", end="")
            elif a[x] == "6":
                print("\033[106m ", end="")
            elif a[x] == "7":
                print("\033[107m ", end="")
            else:
                print(a[x], end="")
        print("\033[0m")