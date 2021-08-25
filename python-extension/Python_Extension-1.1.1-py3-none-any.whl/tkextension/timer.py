import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 6:
    raise SystemExit('This module needs Python 3.6 or more later')

from tkinter import *
from tkinter.messagebox import *
import time

class Timer():
    def __init__(self, window, mode='timer', arg=0):
        self.end = False
        self.tk = window
        self.mode = mode
        if mode == 'timer':
            self.window = Label(window, text=0)
        elif mode == 'down count':
            self.time = arg
            self.window = Label(window, text=self.time)
        elif mode == 'alarm clock':
            self.time = arg
        else:
            raise AttributeError(''' 'Time' object has no attribute '%s' ''' % mode)
    def timer(per1second):
        psecond = per1second % 100
        # Per 1 S
        second = per1second // 100
        while second >= 60:
            second -= 60
        # S
        minute = per1second // 100 // 60
        while minute >= 60:
            minute -= 60
        # Min
        hour = per1second // 100 // 60 // 60
        while hour >= 24:
            hour -= 24
        # H
        day = per1second // 100 // 60 // 60 // 24
        # D
        return '%s : %s : %s : %s : %s' % (day, hour, minute, second, psecond)
    def pack(self, side=None):
        if side != None:
            self.window.pack()
        else:
            self.window.pack(side=side)
    def grid(self, column=None, row=None, columnspan=1, rowspan=1, sticky=None):
        if column != None and row != None:
            if columnspan != 0 and rowspan != 0 and sticky == None:
                self.window.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
            elif columnspan != 0 and rowspan != 0 and sticky != None:
                self.window.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan, sticky=sticky)
            else:
                raise ValueError('Both columnspan and rowspan must be not 0')
        else:
            raise ValueError('Both column and row must be not None')
    def place(self, relx=None, rely=None, relwidth=None, relheight=None, anchor='center'):
        if relx != None and rely != None:
            if relwidth != None and relheight != None:
                self.window.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight, anchor=anchor)
            else:
                self.window.place(relx=relx, rely=rely, anchor=anchor)
        else:
            raise ValueError('Both relx and rely must be not None')
    def mainloop(self):
        if self.mode == 'timer':
            per1second = 0
            while self.end != True:
                self.window.config(text=Timer.timer(per1second))
                self.tk.update()
                time.sleep(0.01)
                per1second += 1
        elif self.mode == 'down count':
            while self.time > 0:
                self.window.config(text=Timer.timer(self.time))
                self.tk.update()
                time.sleep(0.01)
                self.time -= 1
        elif self.mode == 'alarm clock':
            while self.time > 0:
                self.tk.update()
                time.sleep(0.01)
                self.time -= 1
    def stop(self):
        self.end == True
