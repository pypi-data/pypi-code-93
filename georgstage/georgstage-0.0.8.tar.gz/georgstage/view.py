from datetime import datetime, date, timedelta
import logging
import pdb
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import traceback

from dateutil.parser import parse

from georgstage.model import Opgave

logger = logging.getLogger()

NO_DATE = '-'

class View(tk.Tk):
    """docstring for View."""

    PAD = 30
    WIDTH = 12
    LABELS = [
        (Opgave.VAGTHAVENDE_ELEV, 'Vagthavende elev'),
        (Opgave.ORDONNANS, 'Ordonnans'),
        (Opgave.UDKIG, 'Udkig'),
        (Opgave.BJAERGEMAERS, 'Bjærgemærs'),
        (Opgave.RORGAENGER, 'Rorgænger'),
        (Opgave.UDSAETNINGSGAST_A, 'Udsætningsgast A'),
        (Opgave.UDSAETNINGSGAST_B, 'Udsætningsgast B'),
        (Opgave.UDSAETNINGSGAST_C,'Udsætningsgast C'),
        (Opgave.UDSAETNINGSGAST_D,'Udsætningsgast D'),
        (Opgave.UDSAETNINGSGAST_E,'Udsætningsgast E'),
        ((Opgave.PEJLEGAST_A, Opgave.PEJLEGAST_B), 'Pejlegast A/B'),
        (Opgave.DAEKSELEV_I_KABYS, 'Dækselev i kabys')
    ]
    START_TIDER = [0, 4, 8, 12, 16, 20]
    TIDSPUNKTER = ['00 - 04', '04 - 08', '08 - 12', '12 - 16', '16 - 20', '20 - 24']
    ROWS = len(LABELS)
    COLS = 6


    def __init__(self, controller, model):
        super(View, self).__init__()
        self.controller = controller
        self.model = model
        self.title('Georg Stage vagtplanlægger')
        self._make_vars()
        self._make_main_frame()
        self._make_menu()
        self._make_labels()
        self._make_dropdown()
        self._make_entries()
        self.update()


    def main(self):
        logger.info('In main of view ')
        self.mainloop()


    def _refresh_datoer(self, datoer):
        date_list = sorted([d.isoformat() for d in datoer])
        self._dropdown['menu'].delete(0, 'end')
        for dato in date_list:
            self._dropdown['menu'].add_command(label=dato, command=tk._setit(self.current_date, dato))


    def _refresh_vagter(self, vagter):
        # ugly, ugly HU handling
        hu_vagter = {}
        for vagt in vagter:
            key = (vagt.opgave, vagt.vagt_tid)
            #pdb.set_trace()
            if vagt.opgave == Opgave.UDE:
                hu_vagter.setdefault(key, []).append(str(vagt.gast))
            else:
                text = str(vagt.gast)
                self._vars[key].set(text)
        for key, gaster in hu_vagter.items():
            text = ', '.join(gaster)
            self._vars[key].set(text)


    def update(self):
        logger.info('Updating')
        # get model state
        dt = self.model.get_current_dato()
        datoer = self.model.get_datoer()
        if dt is None:
            self.hint.set('Vælg Filer > Åben vagtplan eller Rediger > Opret dato for at fortsætte')
            vagter = []
        else:
            self.hint.set('')
            vagter = self.model[dt]
        # redraw UI
        self._clear_screen()
        self._refresh_datoer(datoer)
        self._refresh_vagter(vagter)
        # set correct date. Stinks a bit. Necessary?
        display_date = dt.isoformat() if dt is not None else NO_DATE
        self.current_date.set(display_date)


    def set_model(self, model):
        self.model = model


    def _get_vars_helper(self):
        for k,v in self._vars.items():
            text = v.get().strip()
            if k[0] == Opgave.UDE:
                for sub_text in text.split(','):
                    yield k, sub_text.strip()
            else:
                yield k, text


    def get_vars(self):
        return list(self._get_vars_helper())


    def get_current_date(self):
        return self.current_date.get()


    def _make_vars(self):
        self._vars = {}
        self.current_date = tk.StringVar(self)
        self.current_date.set(NO_DATE)
        self.current_date.trace('w', self._on_date_selected)
        self.hint = tk.StringVar(self)

    def _clear_screen(self):
        logger.info('Resetting variables')
        for var in self._vars.values():
            var.set('')


    def _make_main_frame(self):
        self.main_frm = tk.Frame(self, bg='White')
        self.main_frm.pack(padx=self.PAD, pady=self.PAD, side=tk.TOP)


    def _make_var(self, key):
        return self._vars.setdefault(key, tk.StringVar(self))


    def _make_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        file_menu = tk.Menu(menu)
        menu.add_cascade(label="Filer", menu=file_menu)
        file_menu.add_command(label="Åben vagtplan", command=self.controller.open_file)
        file_menu.add_command(label="Gem vagtplan", command=self.controller.save_file_as)
        file_menu.add_command(label="Eksporter til word", command=self.controller.export_word)

        rediger_menu = tk.Menu(menu)
        menu.add_cascade(label="Rediger", menu=rediger_menu)
        rediger_menu.add_command(label="Opret ny dato", command=self.controller.create_date)
        rediger_menu.add_command(label="Nulstil valgte dato", command=self.controller.reset_date)
        rediger_menu.add_command(label="Slet valgte dato", command=self.controller.delete_date)

        function_menu = tk.Menu(menu)
        menu.add_cascade(label="Funktioner", menu=function_menu)
        function_menu.add_command(label="Udfyld resten automatisk", command=self.controller.autofill)
        function_menu.add_command(label="Vis statistik", command=self.controller.show_stats)

        help_menu = tk.Menu(menu)
        menu.add_cascade(label="Hjælp", menu=help_menu)
        help_menu.add_command(label="Om Georg Stage vagtplanlægger", command=self.controller.get_help)


    def _make_labels(self):

        tk.Label(self.main_frm, bg='White', textvariable=self.hint, fg='red').grid(row=0, column=1, columnspan=5, sticky=tk.W)

        #tk.Label(self.main_frm, bg='White', text='Tidspunkt').grid(row=1, column=0, sticky=tk.E)
        tk.Label(self.main_frm, bg='White', text='').grid(row=2, column=0, sticky=tk.E)
        for i, (_, label_text) in enumerate(self.LABELS):
            tk.Label(self.main_frm, bg='White', text=label_text).grid(row=i+2, column=0, sticky=tk.E)
        for i, tidspunkt in enumerate(self.TIDSPUNKTER):
            tk.Label(self.main_frm, bg='White', text=tidspunkt, width=self.WIDTH).grid(row=1, column=i+1, sticky=tk.E)
        tk.Label(self.main_frm, bg='White', text='').grid(row=len(self.LABELS)+3, column=0, sticky=tk.E)
        tk.Label(self.main_frm, bg='White', text='Ude/HU').grid(row=len(self.LABELS)+4, column=0, sticky=tk.E)


    def _make_entries(self):

        # vagter, except pejlegast
        def is_gast_or_empty(str):
            return str == '' or (str.isdigit() and 0 < int(str) <= 60)

        vcmd = (self.register(is_gast_or_empty), '%P')

        for i, (opgave, label_text) in enumerate(self.LABELS):
            if opgave == (Opgave.PEJLEGAST_A, Opgave.PEJLEGAST_B):
                # Pejlegase entries
                pejlegast_frame = tk.Frame(self.main_frm)
                tk.Entry(
                    pejlegast_frame,
                    validate='key',
                    validatecommand=vcmd,
                    textvariable=self._make_var((Opgave.PEJLEGAST_A, 12)),
                    justify='right',
                    width=4
                ).pack(side=tk.LEFT)
                tk.Entry(
                    pejlegast_frame,
                    validate='key',
                    validatecommand=vcmd,
                    textvariable=self._make_var((Opgave.PEJLEGAST_B, 12)),
                    justify='right',
                    width=4
                ).pack(side=tk.LEFT)
                pejlegast_frame.grid(row=12, column=4)
            elif opgave == Opgave.DAEKSELEV_I_KABYS:
                for j in range (3):
                    start_tid = self.START_TIDER[j+2]
                    ent = tk.Entry(
                        self.main_frm,
                        validate='key',
                        validatecommand=vcmd,
                        justify='right',
                        textvariable=self._make_var((opgave, start_tid)),
                        width = self.WIDTH
                    ).grid(row=i+2, column=j+3, sticky=tk.E)
            else:
                for j in range(self.COLS):
                    start_tid = self.START_TIDER[j]
                    ent = tk.Entry(
                        self.main_frm,
                        validate='key',
                        validatecommand=vcmd,
                        justify='right',
                        textvariable=self._make_var((opgave, start_tid)),
                        width = self.WIDTH
                    ).grid(row=i+2, column=j+1, sticky=tk.E)
            for i in range(self.COLS):
                start_tid = self.START_TIDER[i]
                tk.Entry(
                    self.main_frm,
                    justify='right',
                    textvariable=self._make_var((Opgave.UDE, start_tid)),
                    width=self.WIDTH
                ).grid(row=len(self.LABELS)+4, column=i+1, sticky=tk.E)


    def _make_dropdown(self):
        date_list = [NO_DATE]
        self.current_date.set(date_list[0])
        self._dropdown = tk.OptionMenu(
            self.main_frm,
            self.current_date,
            *date_list
        )
        self._dropdown.grid(row=0, column=0, sticky=tk.E)


    def show_info(self, header, text):
        messagebox.showinfo(
            header,
            text,
            parent=self.main_frm
        )


    def show_warning(self, title, message):
        messagebox.showwarning(
            title,
            message,
            parent=self.main_frm
        )


    def ask_open_file(self, **kwargs):
        return filedialog.askopenfilename(
            **kwargs,
            parent=self.main_frm
        )


    def ask_save_file_as(self, **kwargs):
        return filedialog.asksaveasfilename(
            **kwargs,
            parent=self.main_frm
        )


    def ask_number(self, header, text):
        number = simpledialog.askinteger(
            header,
            text,
            parent=self.main_frm
        )
        return number


    def ask_string(self, title, prompt, initial_value):
        str = simpledialog.askstring(
            title,
            prompt,
            initialvalue=initial_value,
            parent=self.main_frm
        )
        return str


    def ask_consent(self, header, text):
        return messagebox.askokcancel(
            header,
            text,
            parent=self.main_frm
        )


    def _on_date_selected(self, a, b, c):
        if self.current_date.get() == NO_DATE: return
        new_date = parse(self.current_date.get()).date()
        self.controller.change_date(new_date)
