import tkinter as tk
window=tk.Tk()
def make_tk(name,size):
    window.title(name)
    window.geometry(size)
def make_label(text_,color,ziti):
    tk.Label(window, text=text_, fg=color, font=[ziti,15,"normal"]).pack()
def make_logo(logo):
    window.iconbitmap(logo)
def make_bute(TEXT,hashu):
    w = tk.Button(window, text=TEXT, command=hashu)
    w.place(width=100, height=35)
def hello():#测试函数
    print("hello world")