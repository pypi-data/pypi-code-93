import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 6:
    raise SystemExit('This module needs Python 3.6 or more later')

from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from tkextension.value import *
import pickle
import time

def askvalue(title='', msg='', args=(0, 100)):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).pack()
    if type(args[0]) == type(0):
        sb = Scale(tk, from_=args[0], to=args[1])
    elif type(args[0]) == type('0'):
        sb = Spinbox(tk, values=args, wrap=True)
    else:
        raise TypeError('%s\'s items must be int or string')
    sb.pack()
    Button(tk, text='OK', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = sb.get()
    tk.destroy()
    return get
# Askvalue
def askitem(title='', msg='', items=[], number=1, normal=0):
    tk = Tk()
    tk.title(title)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).place(relx=0.5, rely=0.05, relwidth=1, relheight=0.1, anchor='center')#, selectmode='multiple')
    lb = Listbox(tk)
    lb.place(relx=0.5, rely=0.5, relwidth=0.8, relheight=0.8, anchor='center')
    lb.selection_set(normal)
    Button(tk, text='OK', command=tk.quit).place(relx=0.5, rely=0.95, relwidth=1, relheight=0.1, anchor='center')
    # Window
    for x in range(0, len(items)):
        lb.insert('end', items[x])
    # Load
    tk.mainloop()
    # Mainloop
    finish = False
    get = []
    while not finish:
        tk.mainloop()
        for x in range(0, len(items)):
            if lb.selection_includes(x) == 1:
                get.append(x)
        # Get
        if len(get) == number:
            finish = True
        else:
            showinfo('', 'Choosen items must be %s item(s)' % number)
            get = []
    if get == []:
        get.append(normal)
    # Check & Get
    tk.destroy()
    return get
# Askitem
def askyesnocancel(title='', msg=''):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).grid(column=0, row=0, columnspan=4)
    b1 = Button(tk, text='Cancel')
    b1.grid(column=0, row=1)
    b2 = Button(tk, text='No')
    b2.grid(column=2, row=1)
    b3 = Button(tk, text='Yes')
    b3.grid(column=3, row=1)
    # Tkinter
    b1.bind('<Button-1>', s1)
    b2.bind('<Button-1>', s2)
    b3.bind('<Button-1>', s3)
    # Bind
    while AV.finish == '':
        tk.update()
        time.sleep(0.01)
    # Mainloop
    tk.destroy()
    return AV.finish
# Askyesnocancel
def askanswer(title='', msg=''):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).pack()
    entry = Entry(tk, width=30)
    entry.pack()
    Button(tk, text='Finish', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = entry.get()
    tk.destroy()
    return get
# Askanswer
def controlboard(title='', msg='', item=[('scale', '', 1, 100), ('listbox', '', [1, 2, 3])]):
    tk = Tk()
    tk.title(title)
    tk.minsize(width=100, height=100)
    # Tkinter
    text = Text(tk)
    text.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')
    # Text
    if msg != '':
        text.insert('end', msg)
        text.insert('end', '\n')
    # Label
    window = []
    window_list = []
    for x in item:
        if x[0] == 'scale':
            window.append(Scale(tk, from_=x[2], to=x[3], orient='horizontal'))
            window_list.append('scale')
        elif x[0] == 'listbox':
            window.append(Listbox(tk))
            window_list.append('listbox')
            for y in x[2]:
                window[-1].insert('end', y)
    for x in range(0, len(item)):
        text.insert('end', item[x][1])
        text.insert('end', '\n')
        text.window_create('end', window=window[x])
        text.insert('end', '\n')
    # Scale & Listbox
    button = Button(tk, text='Finish', command=tk.quit)
    text.window_create('end', window=button)
    # Button
    text.config(state='disabled')
    # Window
    tk.mainloop()
    # Mainloop
    result = []
    for x in (0, len(window) - 1):
        if window_list[x] == 'scale':
            result.append(window[x].get())
        elif window_list[x] == 'listbox':
            for y in range(0, len(item[x][2])):
                if window[x].selection_includes(y) == 1:
                    result.append(item[x][2][y])
                    break
            if len(result) < x + 1:
                result.append(item[x][2][0]
                              )
        else:
            raise SystemExit
    tk.destroy()
    return result
# Controlboard
def singlechoice(title='', msg='', args=('a', 'b', 'c')):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).pack()
    window = []
    v = StringVar()
    for x in args:
        window.append(Radiobutton(tk, text=x, variable=v, value=x))
    for x in window:
        x.pack()
    Button(tk, text='Finish', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = v.get()
    tk.destroy()
    return get
# Singlechoice
def singlechoices(title='', msg='', args=(('a', 'b', 'c'), ('e', 'f', 'g'))):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).pack()
    # Label
    window = []
    value_list = []
    lf_list = []
    times = 0
    for x in args:
        value_list.append(StringVar())
        # Value
        lf_list.append(LabelFrame(tk, text=str(times + 1)))
        # LabelFrame
        for y in x:
            window.append(Radiobutton(lf_list[times], text=y, variable=value_list[times], value=y))
        # Tkinter
        times += 1
    for x in window:
        x.pack(side='left')
    for x in lf_list:
        x.pack()
    # Checkbutton
    Button(tk, text='Finish', command=tk.quit).pack()
    # Button
    # Window
    tk.mainloop()
    # Mainloop
    get = []
    for x in value_list:
        get.append(x.get())
    tk.destroy()
    return get
# Singlechoices
def answersheet(title='', msg='', args=[('a', 'b', 'c')], answer=['a'], points=[1]):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).pack()
    # Label
    window = []
    value_list = []
    lf_list = []
    times = 0
    for x in args:
        value_list.append(StringVar())
        # Value
        lf_list.append(LabelFrame(tk, text=str(times + 1)))
        # LabelFrame
        for y in x:
            window.append(Radiobutton(lf_list[times], text=y, variable=value_list[times], value=y))
        # Tkinter
        times += 1
    for x in window:
        x.pack(side='left')
    for x in lf_list:
        x.pack()
    # Checkbutton
    Button(tk, text='Finish', command=tk.quit).pack()
    # Button
    # Window
    tk.mainloop()
    # Mainloop
    get = []
    for x in value_list:
        get.append(x.get())
    tk.destroy()
    # Get
    point = 0
    for x in range(0, len(get)):
        if get[x] == answer[x]:
            point += points[x]
    return [get, point]
# Answersheet
def fastusefile(mode='open', filetypes=[('TXT', '.txt'), ('PY', '.py')], usemode=None, savethings=None):
    if mode == 'open':
        location = askopenfilename(filetypes=filetypes)
        if usemode == 'r' or usemode == None:
            file = open(location)
            text = file.read()
            file.close()
            return (text, location)
        elif usemode == 'rb':
            file = open(location, 'rb')
            text = pickle.load(file)
            file.close()
            return (text, location)
        else:
            raise ValueError('usemode cannot be %s' % usemode)
    elif mode == 'save':
        location = asksaveasfilename(filetypes=filetypes)
        if usemode == 'w' or usemode == None:
            file = open(location, 'w')
            file.write(savethings)
            file.close()
            return location
        elif usemode == 'wb':
            file = open(location, 'wb')
            pickle.dump(savethings, file)
            file.close()
            return location
        else:
            raise ValueError('usemode cannot be %s' % usemode)
# Fastusefile
def create(tkinter_attribute, mode='menu', args=[('1', '<function>')], AddToTkinter=(False, 'grid', 0, 0, 0, 0, 'center'), note='''Args of option menu only takes strings, likes: arg=['a', 'b', 'c']'''):
    tk = tkinter_attribute
    if mode == 'menu':
        a = Menu(tk)
        for x in args:
            a.add_command(label=x[0], command=x[1])
        if AddToTkinter[0] == True:
            tk.config(menu=a)
        return a
    elif mode == 'option menu':
        v = StringVar()
        a = 'OptionMenu(tk, v, '
        for x in arg:
            a = a + '\'' + x + '\''
            if x != args[-1]:
                a = a + ', '
        a = a + ')'
        b = exec(a)
        if AddToTkinter[0] == True:
            if AddToTkinter[1] == 'pack':
                b.pack()
            elif AddToTkinter[1] == 'grid':
                if AddToTkinter[4] == 0:
                    AddToTkinter[4] = 1
                if AddToTkinter[5] == 0:
                    AddToTkinter[5] = 1
                if AddToTkinter[6] == 'center':
                    AddToTkinter[6] = 'w'
                b.grid(column=AddToTkinter[2], row=AddToTkinter[3],
                       columnspan=AddToTkinter[4], rowspan=AddToTkinter[5],
                       sticky=AddToTkinter[6])
            elif AddToTkinter[1] == 'place':
                if AddToTkinter[4] != 0 and AddToTkinter[5] != 0:
                    b.place(relx=AddToTkinter[2], rely=AddToTkinter[3],
                            relwidth=AddToTkinter[4], relheight=AddToTkinter[5],
                            anchor=AddToTkinter[6])
                elif AddToTkinter[4] == 0 and AddToTkinter[5] == 0:
                    b.place(relx=AddToTkinter[2], rely=AddToTkinter[3],
                            anchor=AddToTkinter[6])
                else:
                    raise ValueError('Both relwidth and relheight must be 0 or not 0')
        return b
# Create
