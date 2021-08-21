import datetime
import random
import tkinter as tk
from tkinter import messagebox

WIDTH = 11
TASKS = [
    've_1','ve_2','ve_3','ve_4','ve_5','ve_6',
    'o_1','o_2','o_3','o_4','o_5','o_6',
    'u_1','u_2','u_3','u_4','u_5','u_6',
    'bm_1','bm_2','bm_3','bm_4','bm_5','bm_6',
    'rg_1','rg_2','rg_3','rg_4','rg_5','rg_6',
    'uga_1','uga_2','uga_3','uga_4','uga_5','uga_6',
    'ugb_1','ugb_2','ugb_3','ugb_4','ugb_5','ugb_6',
    'ugc_1','ugc_2','ugc_3','ugc_4','ugc_5','ugc_6',
    'ugd_1','ugd_2','ugd_3','ugd_4','ugd_5','ugd_6',
    'uge_1','uge_2','uge_3','uge_4','uge_5','uge_6',
    'pga','pgb',
    'hu_1','hu_2','hu_3','hu_4','hu_5','hu_6',
    'dk_1','dk_2','dk_3','dk_4','dk_5','dk_6'
]
KEYS = [
    'date',
    'skifte_1','skifte_2','skifte_3','skifte_4','skifte_5','skifte_6',
    'syge'
] + TASKS

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
        self.build(root)
        self.controller.initialize()

    def build(self, root):
        # Static widgets
        tk.Label(root, text='Valgte dag').grid(row=0, column=0, sticky=tk.E)
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

        # Variables
        vars = {key: tk.StringVar() for key in KEYS}
        self._vars = vars

        # Widgets controlled by variables
        tk.Label(root, textvariable=vars['date'], background='gray').grid(row=0, column=1)

        tk.Entry(root, textvariable=vars['skifte_1'], justify='right', width=WIDTH).grid(row=1, column=1)
        tk.Entry(root, textvariable=vars['skifte_2'], justify='right', width=WIDTH).grid(row=1, column=2)
        tk.Entry(root, textvariable=vars['skifte_3'], justify='right', width=WIDTH).grid(row=1, column=3)
        tk.Entry(root, textvariable=vars['skifte_4'], justify='right', width=WIDTH).grid(row=1, column=4)
        tk.Entry(root, textvariable=vars['skifte_5'], justify='right', width=WIDTH).grid(row=1, column=5)
        tk.Entry(root, textvariable=vars['skifte_6'], justify='right', width=WIDTH).grid(row=1, column=6)

        tk.Entry(root, textvariable=vars['ve_1'], justify='right', width=WIDTH).grid(row=3, column=1)
        tk.Entry(root, textvariable=vars['ve_2'], justify='right', width=WIDTH).grid(row=3, column=2)
        tk.Entry(root, textvariable=vars['ve_3'], justify='right', width=WIDTH).grid(row=3, column=3)
        tk.Entry(root, textvariable=vars['ve_4'], justify='right', width=WIDTH).grid(row=3, column=4)
        tk.Entry(root, textvariable=vars['ve_5'], justify='right', width=WIDTH).grid(row=3, column=5)
        tk.Entry(root, textvariable=vars['ve_6'], justify='right', width=WIDTH).grid(row=3, column=6)

        tk.Entry(root, textvariable=vars['o_1'], justify='right', width=WIDTH).grid(row=4, column=1)
        tk.Entry(root, textvariable=vars['o_2'], justify='right', width=WIDTH).grid(row=4, column=2)
        tk.Entry(root, textvariable=vars['o_3'], justify='right', width=WIDTH).grid(row=4, column=3)
        tk.Entry(root, textvariable=vars['o_4'], justify='right', width=WIDTH).grid(row=4, column=4)
        tk.Entry(root, textvariable=vars['o_5'], justify='right', width=WIDTH).grid(row=4, column=5)
        tk.Entry(root, textvariable=vars['o_6'], justify='right', width=WIDTH).grid(row=4, column=6)

        tk.Entry(root, textvariable=vars['u_1'], justify='right', width=WIDTH).grid(row=5, column=1)
        tk.Entry(root, textvariable=vars['u_2'], justify='right', width=WIDTH).grid(row=5, column=2)
        tk.Entry(root, textvariable=vars['u_3'], justify='right', width=WIDTH).grid(row=5, column=3)
        tk.Entry(root, textvariable=vars['u_4'], justify='right', width=WIDTH).grid(row=5, column=4)
        tk.Entry(root, textvariable=vars['u_5'], justify='right', width=WIDTH).grid(row=5, column=5)
        tk.Entry(root, textvariable=vars['u_6'], justify='right', width=WIDTH).grid(row=5, column=6)

        tk.Entry(root, textvariable=vars['bm_1'], justify='right', width=WIDTH).grid(row=6, column=1)
        tk.Entry(root, textvariable=vars['bm_2'], justify='right', width=WIDTH).grid(row=6, column=2)
        tk.Entry(root, textvariable=vars['bm_3'], justify='right', width=WIDTH).grid(row=6, column=3)
        tk.Entry(root, textvariable=vars['bm_4'], justify='right', width=WIDTH).grid(row=6, column=4)
        tk.Entry(root, textvariable=vars['bm_5'], justify='right', width=WIDTH).grid(row=6, column=5)
        tk.Entry(root, textvariable=vars['bm_6'], justify='right', width=WIDTH).grid(row=6, column=6)

        tk.Entry(root, textvariable=vars['rg_1'], justify='right', width=WIDTH).grid(row=7, column=1)
        tk.Entry(root, textvariable=vars['rg_2'], justify='right', width=WIDTH).grid(row=7, column=2)
        tk.Entry(root, textvariable=vars['rg_3'], justify='right', width=WIDTH).grid(row=7, column=3)
        tk.Entry(root, textvariable=vars['rg_4'], justify='right', width=WIDTH).grid(row=7, column=4)
        tk.Entry(root, textvariable=vars['rg_5'], justify='right', width=WIDTH).grid(row=7, column=5)
        tk.Entry(root, textvariable=vars['rg_6'], justify='right', width=WIDTH).grid(row=7, column=6)

        tk.Entry(root, textvariable=vars['uga_1'], justify='right', width=WIDTH).grid(row=8, column=1)
        tk.Entry(root, textvariable=vars['uga_2'], justify='right', width=WIDTH).grid(row=8, column=2)
        tk.Entry(root, textvariable=vars['uga_3'], justify='right', width=WIDTH).grid(row=8, column=3)
        tk.Entry(root, textvariable=vars['uga_4'], justify='right', width=WIDTH).grid(row=8, column=4)
        tk.Entry(root, textvariable=vars['uga_5'], justify='right', width=WIDTH).grid(row=8, column=5)
        tk.Entry(root, textvariable=vars['uga_6'], justify='right', width=WIDTH).grid(row=8, column=6)

        tk.Entry(root, textvariable=vars['ugb_1'], justify='right', width=WIDTH).grid(row=9, column=1)
        tk.Entry(root, textvariable=vars['ugb_2'], justify='right', width=WIDTH).grid(row=9, column=2)
        tk.Entry(root, textvariable=vars['ugb_3'], justify='right', width=WIDTH).grid(row=9, column=3)
        tk.Entry(root, textvariable=vars['ugb_4'], justify='right', width=WIDTH).grid(row=9, column=4)
        tk.Entry(root, textvariable=vars['ugb_5'], justify='right', width=WIDTH).grid(row=9, column=5)
        tk.Entry(root, textvariable=vars['ugb_6'], justify='right', width=WIDTH).grid(row=9, column=6)

        tk.Entry(root, textvariable=vars['ugc_1'], justify='right', width=WIDTH).grid(row=10, column=1)
        tk.Entry(root, textvariable=vars['ugc_2'], justify='right', width=WIDTH).grid(row=10, column=2)
        tk.Entry(root, textvariable=vars['ugc_3'], justify='right', width=WIDTH).grid(row=10, column=3)
        tk.Entry(root, textvariable=vars['ugc_4'], justify='right', width=WIDTH).grid(row=10, column=4)
        tk.Entry(root, textvariable=vars['ugc_5'], justify='right', width=WIDTH).grid(row=10, column=5)
        tk.Entry(root, textvariable=vars['ugc_6'], justify='right', width=WIDTH).grid(row=10, column=6)

        tk.Entry(root, textvariable=vars['ugd_1'], justify='right', width=WIDTH).grid(row=11, column=1)
        tk.Entry(root, textvariable=vars['ugd_2'], justify='right', width=WIDTH).grid(row=11, column=2)
        tk.Entry(root, textvariable=vars['ugd_3'], justify='right', width=WIDTH).grid(row=11, column=3)
        tk.Entry(root, textvariable=vars['ugd_4'], justify='right', width=WIDTH).grid(row=11, column=4)
        tk.Entry(root, textvariable=vars['ugd_5'], justify='right', width=WIDTH).grid(row=11, column=5)
        tk.Entry(root, textvariable=vars['ugd_6'], justify='right', width=WIDTH).grid(row=11, column=6)

        tk.Entry(root, textvariable=vars['uge_1'], justify='right', width=WIDTH).grid(row=12, column=1)
        tk.Entry(root, textvariable=vars['uge_2'], justify='right', width=WIDTH).grid(row=12, column=2)
        tk.Entry(root, textvariable=vars['uge_3'], justify='right', width=WIDTH).grid(row=12, column=3)
        tk.Entry(root, textvariable=vars['uge_4'], justify='right', width=WIDTH).grid(row=12, column=4)
        tk.Entry(root, textvariable=vars['uge_5'], justify='right', width=WIDTH).grid(row=12, column=5)
        tk.Entry(root, textvariable=vars['uge_6'], justify='right', width=WIDTH).grid(row=12, column=6)

        frame = tk.Frame()
        tk.Entry(frame, textvariable=vars['pga'], justify='right', width=4).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=vars['pgb'], justify='right', width=4).pack(side=tk.LEFT)
        frame.grid(row=13, column=3)

        tk.Entry(root, textvariable=vars['hu_1'], justify='right', width=WIDTH).grid(row=14, column=1)
        tk.Entry(root, textvariable=vars['hu_2'], justify='right', width=WIDTH).grid(row=14, column=2)
        tk.Entry(root, textvariable=vars['hu_3'], justify='right', width=WIDTH).grid(row=14, column=3)
        tk.Entry(root, textvariable=vars['hu_4'], justify='right', width=WIDTH).grid(row=14, column=4)
        tk.Entry(root, textvariable=vars['hu_5'], justify='right', width=WIDTH).grid(row=14, column=5)
        tk.Entry(root, textvariable=vars['hu_6'], justify='right', width=WIDTH).grid(row=14, column=6)

        tk.Entry(root, textvariable=vars['dk_1'], justify='right', width=WIDTH).grid(row=15, column=1)
        tk.Entry(root, textvariable=vars['dk_2'], justify='right', width=WIDTH).grid(row=15, column=2)
        tk.Entry(root, textvariable=vars['dk_3'], justify='right', width=WIDTH).grid(row=15, column=3)
        tk.Entry(root, textvariable=vars['dk_4'], justify='right', width=WIDTH).grid(row=15, column=4)
        tk.Entry(root, textvariable=vars['dk_5'], justify='right', width=WIDTH).grid(row=15, column=5)
        tk.Entry(root, textvariable=vars['dk_6'], justify='right', width=WIDTH).grid(row=15, column=6)
        tk.Entry(root, textvariable=vars['syge'], justify='right', width=WIDTH).grid(row=16, column=1)

        # Buttons
        tk.Button(root, text='Forrige dag', command=self.controller.prev_day).grid(row=0, column=2)
        tk.Button(root, text='Næste dag', command=self.controller.next_day).grid(row=0, column=3)
        tk.Button(root, text='Load', command=self.controller.load).grid(row=0, column=5)
        tk.Button(root, text='Save', command=self.controller.save).grid(row=0, column=6)
        tk.Button(root, text='Udfyld resten', command=self.controller.fill_day).grid(row=17, column=5)
        tk.Button(root, text='Eksporter', command=self.controller.export_day).grid(row=17, column=6)

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
        pass

    def save(self):
        pass

    def initialize(self):
        print('initialize called')
        date = to_datestr(datetime.date.today())
        day = self.model.get_day(date)
        self.view.set_vars(day)

    def change_day(self, num_days):
        cur_day = self.view.get_vars()
        cur_date = cur_day['date']
        self.model.set_day(cur_date, cur_day)
        new_date = change_strdate(cur_date, num_days=num_days)
        new_day = self.model.get_day(new_date)
        self.view.set_vars(new_day)

    def next_day(self):
        print('next_day called')
        self.change_day(1)

    def prev_day(self):
        print('prev_day called')
        self.change_day(-1)

    def reset(self):
        print('reset called')

    def fill_day(self):
        print('fill_day called')
        vars = self.view.get_vars()
        date = vars['date']
        self.model.set_day(date, vars)
        self.model.fill_day(date)
        self.view.set_vars(self.model.get_day(date))

    def export_day(self):
        print('export_day called')

    def close(self):
        print('close called')

class Model():

    def __init__(self, days=None):
        self.days = days or {}

    def get_day(self, date):
        if date in self.days:
            return self.days[date]
        else:
            day = {key: '' for key in KEYS}
            day['date'] = date
            for key, s in self.suggest_skifter(date).items():
                day[key] = s
            self.days[date] = day
            return self.days[date]

    def set_day(self, date, vars):
        self.days[date] = vars

    def fill_day(self, date):
        day = self.days[date]
        for key in TASKS:
            if day[key] == '':
                day[key] = '-1'

    def suggest_skifter(self, date):
        return {f'skifte_{i+1}': str(1 + i%3) for i in range(6)}

if __name__=='__main__':
    root = tk.Tk()
    root.title('Georg Stage Søvagt - version 0.9')
    model = Model()
    controller = Controller(model)
    view = View(root, controller)
    tk.mainloop()
