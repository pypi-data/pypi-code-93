from turtle import*
from time import*
#定义3D画笔               x y z 焦距
#z不能为0
def go_3(x,y,z,focal_length):
    goto(focal_length*(x/z),focal_length*(y/z))
#生成金箍棒    长 旋转次数 旋转角度
def summon_GC(l,rn,j):
    color("red")
    forward(0-(l/4))
    color("yellow")
    forward(0-(l/4))
    penup()
    forward(l/2)
    pendown()
    color("red")
    forward(l/4)
    color("yellow")
    forward(l/4)
    if rn == 0 or j == 0:
        pass
    else:
        Screen().tracer(0)
        for i in range(rn):
            clear()
            color("red")
            forward(0-(l/4))
            color("yellow")
            forward(0-(l/4))
            penup()
            forward(l/2)
            pendown()
            color("red")
            forward(l/4)
            color("yellow")
            forward(l/4)
            left(j)
            Screen().update()
#定义计时器 持续时间 间隔秒数  长度
def timecount(time,spit,spittime,h):
    speed(0)
    ttttttt = 0
    while ttttttt < time:
        ttttttt += spittime
        sleep(spit)
        print(ttttttt)
        forward(h*spittime)
#画五角星    x坐标 y坐标 大小 是否填充，颜色
def draw_star(x,y,h,fill,c):
    speed(0)
    ht()
    pencolor(c)
    color(c)
    if fill == 0:
        penup()
        goto(x,y)
        forward(150)
        pendown()
        for i in range(5):
            forward(h)
            right(144)
    else:
        penup()
        goto(x,y)
        forward(150)
        pendown()
        begin_fill()
        for i in range(5):
            forward(h)
            right(144)
        end_fill()
#闪光字 内容 时间
def colortext(text, t):
    import random
    colcolcol = [31, 32, 33, 34, 35, 36, 37, 91, 92, 93, 94, 95, 96, 97]
    import time
    import sys
    times = int(t / 0.1)
    for i in range(times):
        print("\033[{}m{}".format(random.choice(colcolcol), text))
        time.sleep(0.1)
        sys.stdout.write('\033[2J\033[00H')