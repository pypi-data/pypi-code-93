# -*- coding: utf-8 -*-
"""
使用turtle模块的太阳系模拟程序

快捷键:
按Ctrl+“+”或Ctrl+“-”进行缩放。
按↑，↓，←，→键移动。
按“+”或“-”键增加或者降低速度。
单击屏幕开启或关闭轨道显示。
单击行星即可跟随该行星。
"""
try:
    from time import perf_counter
# 兼容 Python 2 与 Python 3
except ImportError:from time import clock as perf_counter
from random import randrange
import math,turtle,_thread
from turtle import *

_thread.start_new_thread(lambda:exec("import matplotlib.pyplot as plt",globals()),())

Vec=Vec2D
try:
    from tkinter import TclError
except ImportError:
    from Tkinter import TclError

__author__="七分诚意 qq:3076711200"
__email__="3416445406@qq.com"
__version__="1.1.1"

G = 8
PLANET_SIZE=8 # 像素

# 各个行星的质量
SUN_MASS=1000000

MERCURY_MASS=125
VENUS_MASS=3000
EARTH_MASS=4000
MOON_MASS=1
MARS_MASS=600
PHOBOS_MASS=2
AST_MASS=2

JUPITER_MASS=7000
SATURN_MASS=6000
URANUS_MASS=9000
NEPTUNE_MASS=8000

scr=None
l=[]

class GravSys:
    # 引力系统
    __slots__=['planets', 'removed_planets', 't', 'dt', 'frameskip',
               'scale', 'scr_x', 'scr_y', 'key_x', 'key_y',
               'show_fps','__last_time','writer','fps','following']
    def __init__(self):
        self.planets = []
        self.removed_planets=[]
        self.t = 0
        self.dt = 0.0015 # 速度
        #frameskip: 程序在绘制一帧之前跳过的帧数
        self.frameskip=3
        self.scale=1
        self.scr_x=self.key_x=0
        self.scr_y=self.key_y=0
        self.show_fps=True;self.fps=20
        self.writer=Turtle()
        self.writer.hideturtle()
        self.writer.penup()
        self.writer.color("white")
        #following: 跟随某个行星
        self.following=None
    def init(self):
        for p in self.planets:
            p.init()
    def start(self):
        while True:
            self.__last_time=perf_counter()
            # 计算行星的位置
            for _ in range(self.frameskip):
                self.t += self.dt
                for p in self.planets:
                    p.step()
            if self.following!=None:
                self.scr_x=-self.following._pos[0]+self.key_x
                self.scr_y=-self.following._pos[1]+self.key_y
            else:
                self.scr_x=self.key_x
                self.scr_y=self.key_y
            # 刷新行星
            for p in self.planets:
                p.update()
            update()
            l.append(self.planets[0].distance(self.planets[1]))

            self.fps=1/(perf_counter()-self.__last_time)

            # 显示帧率
            if self.show_fps:
                self.writer.clear()
                self.writer.goto(
                    scr.window_width()//2-90,scr.window_height()//2-35
                )
                self.writer.write(
                    "fps:%d" % self.fps,
                    font = (None,12)
                )
    def follow(self,planet):
        if self.following:
            self.following.onfollow(False)
        self.following=planet
        self.key_x=self.key_y=0
        planet.onfollow(True)
        scr.ontimer(self.clear_scr, int(1000/self.fps))
    def increase_speed(self,event):
        self.dt+=0.001
    def decrease_speed(self,event):
        self.dt-=0.001
    def zoom(self,event):
        if event.keysym=="equal":
            # 放大
            self.scale*=1.33
        else:
            # 缩小
            self.scale/=1.33
        for planet in self.planets:
            scale=planet._size*self.scale
            if planet.keep_on_scr:
                planet.shapesize(max(0.08,scale))
            else:
                planet.shapesize(scale)
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        self.clear_removed_planets()

    def clear_scr(self):
        for planet in self.planets:
            planet.clear()

    def up(self,event=None):
        self.key_y -= 25 / self.scale
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        self.clear_removed_planets()
    def down(self,event=None):
        self.key_y += 25 / self.scale
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        self.clear_removed_planets()
    def left(self,event=None):
        self.key_x += 25 / self.scale
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        self.clear_removed_planets()
    def right(self,event=None):
        self.key_x -= 25 / self.scale
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        self.clear_removed_planets()
    def switchpen(self,x,y):
        targets=[]
        for planet in self.planets:
            psize=max(planet.getsize()*1.375, 2)
            if abs(planet.xcor()-x) <= psize \
               and abs(planet.ycor()-y) <= psize \
               and planet is not self.following:
                targets.append(planet)

            if not planet.has_orbit:
                continue
            if planet.isdown():
                planet.penup()
            else:planet.pendown()
            planet.clear()

        if targets:self.follow(max(targets,key=lambda p:p.m))
        self.clear_removed_planets()

    def clear_removed_planets(self):
        for planet in self.removed_planets:
            planet.clear()
        self.removed_planets=[]

class Star(Turtle):
    def __init__(self, gravSys, m, x, v,
                 shape,shapesize=1,orbit_color=None,has_orbit=True,
                 parent=None,keep_on_scr=False,rotation=None,sun=None):
        Turtle.__init__(self)
        self.shape(shape)
        self._shape=shape
        self._size=shapesize
        self.shapesize(shapesize)
        if orbit_color is not None:
            self.pencolor(orbit_color)
        self.penup()
        self.m = m
        self._pos=x
        self.setpos(x)
        self.v = v
        self.has_orbit=has_orbit
        self.gravSys = gravSys
        self.keep_on_scr = keep_on_scr
        self.rotation=rotation
        self.sun=sun or (self.gravSys.planets[0] if len(self.gravSys.planets) else None)
        gravSys.planets.append(self)
        self.resizemode("user")
        self.setundobuffer(None)

        self.children=[]
        if parent:
            parent.children.append(self)
    def init(self):
        if self.has_orbit:
            self.pendown()
        dt = self.gravSys.dt
        self.a = self.acc()
        self.v = self.v + 0.5*dt*self.a
    def acc(self):
        # 计算行星的加速度
        a = Vec(0,0)
        for planet in self.gravSys.planets:
            if planet is not self:
                v = planet._pos-self._pos
                try:
                    a += (G*planet.m/abs(v)**3)*v
                except ZeroDivisionError:pass
        return a
    def step(self):
        # 计算行星位置
        dt = self.gravSys.dt
        self._pos += dt*self.v

        a = self.acc()
        self.v = self.v + dt*a
    def update(self):
        self.setpos((self._pos+(self.gravSys.scr_x,
                                self.gravSys.scr_y))*self.gravSys.scale)
        if self.rotation is not None:
            self.left(self.rotation*self.gravSys.dt)
        elif self.sun:
            self.setheading(self.towards(self.sun))
        if abs(self._pos[0])>10000 or abs(self._pos[1])>10000:
            self.gravSys.removed_planets.append(self)
            self.gravSys.planets.remove(self)
            self.hideturtle()
    def getsize(self):
        return self._stretchfactor[0]*PLANET_SIZE*2
    def distance(self,other):
        return math.hypot(self._pos[0]-other._pos[0],
                          self._pos[1]-other._pos[1])
    def grav(self,other):
        # 计算两行星间的引力, F = G *m1*m2 / r**2
        r=math.hypot(self._pos[0]-other._pos[0],
                     self._pos[1]-other._pos[1])
        return G *self.m*other.m / r**2
    def tide(self,other,radius=None):
        # 计算行星对自身的潮汐力
        radius=radius or self.getsize() / 2
        r1=self.distance(other)-radius
        r2=self.distance(other)+radius
        return G *self.m*other.m / r1**2 - \
               G *self.m*other.m / r2**2
    def onfollow(self,arg): # arg:True或False
        for p in self.children:
            p.has_orbit=arg
            if arg and self.isdown():
                p.pendown()
            else:p.penup()
        self.keep_on_scr=True

    def __repr__(self):
        return object.__repr__(self)[:-1] + " shape: %s"%self._shape + '>'

class RoundStar(Star):
    def __init__(self,gravSys, m, x, v,
                 shapesize=1,orbit_color=None,has_orbit=True):
        Star.__init__(self,gravSys, m, x, v,
                     "blank",shapesize,orbit_color,has_orbit,rotation=0)
    def init(self):
        Star.init(self)
        self.setheading=lambda angle:None
    def update(self):
        Star.update(self)
        self.clear()
        size=self.getsize()
        if size>0.04:
            px=3 if size>0.2 else 2
            self.dot(max(size,px))

class Sun(Star):
    # 太阳不移动, 固定在引力系统的中心
    def __init__(self,*args,**kw):
        Star.__init__(self,*args,**kw)
        self.keep_on_scr=True
    def step(self):
        pass
    def update(self):
        self.setpos((self._pos+(self.gravSys.scr_x,
                                self.gravSys.scr_y))*self.gravSys.scale)
        if self.rotation is not None:
            self.left(self.rotation*self.gravSys.dt)
        #Star.update(self)

def main():
    global scr
    scr=Screen()
    scr.screensize(10000,10000)
    try:
        scr._canvas.master.state("zoomed")
    except:pass
    scr.bgcolor("black")
    scr.tracer(0,0)

    # create compound turtleshape for planets
    s = Turtle()
    s.reset()
    s.ht()
    s.pu()
    s.fd(PLANET_SIZE)
    s.lt(90)
    s.begin_poly()
    s.circle(PLANET_SIZE, 180,steps=16)
    s.end_poly()
    _light = s.get_poly()
    s.begin_poly()
    s.circle(PLANET_SIZE, 180,steps=16)
    s.end_poly()
    _dark = s.get_poly()
    s.begin_poly()
    s.circle(PLANET_SIZE,steps=16)
    s.end_poly()
    _circle = s.get_poly()
    update()
    s.hideturtle()
    def create_shape(screen,name,light,dark=None): #,gh=False):
        shape = Shape("compound")
        if dark is not None:
            shape.addcomponent(_light,light)
            shape.addcomponent(_dark,dark)
        else:
            shape.addcomponent(_circle,light)
        screen.register_shape(name, shape)

    create_shape(scr,"sun","yellow")
    create_shape(scr,"earth","blue","blue4")
    create_shape(scr,"moon","gray70","grey30")

    # setup gravitational system
    gs = GravSys()
    star1=Star(gs,SUN_MASS/2,Vec(-20,0),Vec(0,223),
               "sun",1.2,"yellow")
    star2=Star(gs,SUN_MASS/2,Vec(20,0),Vec(0,-223),
               "sun",1.2,"yellow")

    # 地球
    earth = Star(gs,1, Vec(260,0), Vec(0,173),
                 "earth",0.8, "blue",sun=None)
    earth2 = Star(gs,1, Vec(-260,0), Vec(0,-173),
                 "earth",0.8, "blue",sun=None)
    earth3 = Star(gs,1, Vec(-70,0), Vec(0,-360),
                 "earth",0.8, "blue",sun=None)
    moon1 = Star(gs,1,Vec(-28,0),Vec(0,900),
               "moon",0.5,"gray30")

    # 绑定键盘事件
    cv=scr.getcanvas()
    cv.bind_all("<Key-Up>",gs.up)
    cv.bind_all("<Key-Down>",gs.down)
    cv.bind_all("<Key-Left>",gs.left)
    cv.bind_all("<Key-Right>",gs.right)
    cv.bind_all("<Key-equal>",gs.increase_speed)
    cv.bind_all("<Key-minus>",gs.decrease_speed)
    cv.bind_all("<Control-Key-equal>",gs.zoom) #Ctrl+"+"
    cv.bind_all("<Control-Key-minus>",gs.zoom) #Ctrl+"-"
    #scr.tracer(1,0)
    

    scr.onclick(gs.switchpen)
    #gs.follow(earth)
    gs.init()
    try:gs.start()
    except (Terminator,TclError):pass
    globals().update(locals())
    _plot()

def _plot():
    plt.plot(range(len(l)),l)
    plt.show()

if __name__ == '__main__':
    main()
    if scr._RUNNING:mainloop()
