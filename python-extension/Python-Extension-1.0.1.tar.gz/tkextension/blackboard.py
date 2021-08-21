import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 6:
    raise SystemExit('This module needs Python 3.6 or more later')

from tkinter import *
from tkinter.colorchooser import *
from tkextension import *

class BlackBoard():
    def __init__(self, tkinter_attribute, width=200, height=100, bg='#ffffff'):
        self.color = 'black'
        self.width = 1
        # Value
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        self.canvas = Canvas(self.frame, width=width, height=height, bg=bg)
        self.canvas.pack()
        lb = LabelFrame(self.frame, text='Tools')
        lb.pack()
        self.colorchoose = Button(lb, text='A', command=self.colorchoose)
        self.colorchoose.grid(column=0, row=0)
        Button(lb, text='Width', command=self.width).grid(column=0, row=1)
        self.entry = Text(lb, width=int(width / 10), height=2)
        self.entry.grid(column=1, row=0)
        self.upload = Button(lb, text='Show')
        self.upload.grid(column=1, row=1)
        # Window
        self.tk.bind_all('<Motion>', self.regrid)
        self.canvas.bind('<Button-1>', self.draw)
        # Bind
    def regrid(self, event):
        self.tk.grid()
    def draw(self, event):
        x1, y1 = (event.x - self.width), (event.y - self.width)
        x2, y2 = (event.x + self.width), (event.y + self.width)
        self.canvas.create_oval(x1, y1, x2, y2, fill=self.color)
    def pack(self, **kw):
        self.frame.pack(**kw)
    def grid(self, **kw):
        self.frame.grid(**kw)
    def place(self, **kw):
        self.frame.place(**kw)
    def colorchoose(self):
        self.color = askcolor()
        self.color = self.color[1]
        self.colorchoose.config(text='A', fg=self.color)
    def width(self):
        self.width = askvalue('', 'Width', (1, 100))
    def text(self):
        self.label = Label(self.frame, text='Select where to display the text')
        self.label.pack()
        self.canvas.bind('<Button-1>', self.show_text)
        self.tk.update()
    def show_text(self, event):
        self.label.pack_forget()
        self.canvas.create_text(event.x, event.y, self.entry.get(1.0, 'end'))
        self.tk.update()

tk = Tk()
a = BlackBoard(tk)
a.pack()
