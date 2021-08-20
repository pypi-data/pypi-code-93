from tkinter import *;import tkinter;from tkinter import messagebox,ttk,filedialog
class 窗口(tkinter.Tk):
    def __init__(self):
        Tk.__init__(self)
    主循环=Tk.mainloop
    标题=Tk.title
    图标=Tk.iconbitmap
    大小和位置=Tk.geometry
    属性=Tk.attributes
    协议=Tk.protocol
class 标签(Label):
    def __init__(self,容器,文本='',图片=None,字体=None):
        Label.__init__(master=容器,text=文本,image=图片,font=字体)
    居中显示=Label.pack
    在指定行显示=Label.grid
    设置xy显示=Label.place
class 按钮(Label):
    def __init__(self,容器,文本='',图片=None,字体=None):
        Button.__init__(master=容器,text=文本,image=图片,font=字体)
    居中显示=Button.pack
    在指定行显示=Button.grid
    设置xy显示=Button.place
