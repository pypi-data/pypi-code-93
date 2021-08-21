import datetime
import random
import tkinter as tk
from tkinter import messagebox, filedialog, Menu

WIDTH = 10

def to_datestr(date):
    return f'{date.year}/{str(date.month).zfill(2)}/{str(date.day).zfill(2)}'

def from_datestr(datestr):
    return datetime.datetime.strptime(datestr, '%Y/%m/%d').date()

def change_strdate(strdate, num_days=1):
    new_date = from_datestr(strdate) + datetime.timedelta(days=num_days)
    return to_datestr(new_date)

class View():

    def __init__(self, root, controller):
        self.controller = controller
        self.controller.view = self
        self._vars = {}
        self.build(root)
        self.controller.initialize()
        self.open_file = None
        self.current_day = None
        self.model = GeorgStage(vagter=[])

    def build(self, root):
        # Create menu
        menu = Menu(root)
        root.config(menu=menu)
        fileMenu = Menu(menu)
        menu.add_cascade(label="Filer", menu=fileMenu)
        functionMenu = Menu(menu)
        menu.add_cascade(label="Funktioner", menu=functionMenu)
        fileMenu.add_command(label="Indlæs togt", command=self.controller.load)
        fileMenu.add_command(label="Gem togt", command=self.controller.save)
        functionMenu.add_command(label="Udfyld resten", command=self.controller.fill_day)

        # Static widgets
        tk.Label(root, text='Dato (YYYY-MM-DD)').grid(row=0, column=0, sticky=tk.E)
        tk.Label(root, text='Skifte').grid(row=1, column=0, sticky=tk.E)
        tk.Label(root, text='Tidsrum').grid(row=2, column=0, sticky=tk.E)
        # tider
        tk.Label(root, text='08-12', width=WIDTH).grid(row=2, column=1)
        tk.Label(root, text='12-16', width=WIDTH).grid(row=2, column=2)
        tk.Label(root, text='16-20', width=WIDTH).grid(row=2, column=3)
        tk.Label(root, text='20-24', width=WIDTH).grid(row=2, column=4)
        tk.Label(root, text='00-04', width=WIDTH).grid(row=2, column=5)
        tk.Label(root, text='04-08', width=WIDTH).grid(row=2, column=6)
        # resten
        tk.Label(root, text='Vagthavende ELEV').grid(row=3, column=0, sticky=tk.E)
        tk.Label(root, text='Ordonnans').grid(row=4, column=0, sticky=tk.E)
        tk.Label(root, text='Udkig').grid(row=5, column=0, sticky=tk.E)
        tk.Label(root, text='Bjærgemærs').grid(row=6, column=0, sticky=tk.E)
        tk.Label(root, text='Rorgænger').grid(row=7, column=0, sticky=tk.E)
        tk.Label(root, text='Udsætningsgast A').grid(row=8, column=0, sticky=tk.E)
        tk.Label(root, text='Udsætningsgast B').grid(row=9, column=0, sticky=tk.E)
        tk.Label(root, text='Udsætningsgast C').grid(row=10, column=0, sticky=tk.E)
        tk.Label(root, text='Udsætningsgast D').grid(row=11, column=0, sticky=tk.E)
        tk.Label(root, text='Udsætningsgast E').grid(row=12, column=0, sticky=tk.E)
        tk.Label(root, text='Pejlegast A/B').grid(row=13, column=0, sticky=tk.E)
        tk.Label(root, text='HU').grid(row=14, column=0, sticky=tk.E)
        tk.Label(root, text='Dækselev i kabys').grid(row=15, column=0, sticky=tk.E)
        tk.Label(root, text='Syge (f.eks 1,2,3)').grid(row=16, column=0, sticky=tk.E)


        # Widgets controlled by variables
        tk.Entry(root, textvariable=tk.StringVar(), width=WIDTH).grid(row=0, column=1)

        tk.Label(root, textvariable=tk.StringVar(), width=WIDTH).grid(row=2, column=1)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=3, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=3, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=3, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=3, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=3, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=3, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=4, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=4, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=4, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=4, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=4, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=4, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=5, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=5, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=5, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=5, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=5, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=5, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=6, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=6, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=6, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=6, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=6, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=6, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=7, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=7, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=7, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=7, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=7, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=7, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=8, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=8, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=8, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=8, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=8, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=8, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=9, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=9, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=9, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=9, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=9, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=9, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=10, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=10, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=10, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=10, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=10, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=10, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=11, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=11, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=11, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=11, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=11, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=11, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=12, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=12, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=12, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=12, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=12, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=12, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=13, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=13, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=13, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=13, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=13, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=13, column=6)

        frame = tk.Frame()
        tk.Entry(frame, textvariable=tk.StringVar(), justify='right', width=4).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=tk.StringVar(), justify='right', width=4).pack(side=tk.LEFT)
        frame.grid(row=13, column=3)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=14, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=14, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=14, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=14, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=14, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=14, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=15, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=15, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=15, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=15, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=15, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=15, column=6)

        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=16, column=1)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=16, column=2)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=16, column=3)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=16, column=4)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=16, column=5)
        tk.Entry(root, textvariable=tk.StringVar(), justify='right', width=WIDTH).grid(row=16, column=6)


        # Buttons
        tk.Button(root, text='Gå til dag', command=self.controller.go_to_day).grid(row=0, column=2)

    def set_vars(self, vars):
        # set date
        for key, value in vars.items():
            assert(key in self._vars)
            self._vars[key].set(value)

    def get_vars(self):
        return {k:v.get() for k,v in self._vars.items()}


class Controller():

    def __init__(self, model):
        self.view = None
        self.model = model

    def load(self):
        filename = filedialog.askopenfilename()
        print(f'load called: {filename}')

    def save(self):
        print('save called')

    def initialize(self):
        print('initialize called')

    def go_to_day(self):
        print('go_to_day called')

    def fill_day(self):
        print('fill_day called')
        vars = self.view.get_vars()
        for var in vars:
            print(var)
        #date = vars['date']
        self.view.set_vars(vars)

    def close(self):
        print('close called')

if __name__=='__main__':
    root = tk.Tk()
    root.title('Georg Stage Søvagt - version 0.8')
    controller = Controller(None)
    view = View(root, controller)
    tk.mainloop()
