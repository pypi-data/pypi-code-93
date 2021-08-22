import os


from tkinter import *

from tkinter import Tk, ttk, filedialog


class TkMixin(object):

    tk = Tk()

    def title(self, *args, **kwargs):
        TkMixin.tk.title(*args, *kwargs)

    def geometry(self, *args, **kwargs):
        TkMixin.tk.geometry(*args, *kwargs)

    def mainloop(self, *args, **kwargs):
        TkMixin.tk.mainloop(*args, *kwargs)

    def quit(self):
        TkMixin.tk.destroy()

    def resize_grip(self):
        parent_frame = self.parent_frame()
        parent_frame.resizable(True, True)
        sizegrip = ttk.Sizegrip(parent_frame)
        sizegrip.pack(side=RIGHT, anchor=SE)


class Tile(TkMixin):

    TkMixin.title(None, "pyTile / tk")

    def __init__(self, _parent=None, **kwargs):
        self._kwargs = kwargs
        self._frame = []

        self.frame = None
        self.set_parent(_parent)

        self.__init__internal__()

    def set_parent(self, parent):
        self._parent = parent

    def __init__internal__(self):
        pass

    def __init__tile__(self):
        if self.frame == None:
            self.frame = ttk.Frame(
                self.parent_frame(),
            )

    def __end__tile__(self):
        # todo rename this ...
        for f in self._frame:
            f.forget()
        self._frame = []

    def parent_frame(self):
        return self._parent.frame if type(self._parent) == Tile else self._parent

    def add(self, elem):
        self.__init__tile__()
        self._add(
            elem.create_element(self.frame),
        )

    def _add(self, elem):
        self.__add(elem, self._frame)

    def __add(self, elem, target):
        if elem == None:
            return
        if type(elem) == list:
            for el in elem:
                self.__add(el, target)
        else:
            target.append(elem)

    def _build(self):
        self.__init__tile__()
        self._add(
            self.create_element(self.frame),
        )

    def create_element(self, frame):
        pass

    def layout(self):
        self.__end__tile__()
        self._build()
        self.do_layout()

    def do_layout(self):
        self._do_layout()
        self.frame.pack(anchor=W)

    def _do_layout(self):
        for el in self._frame:
            if isinstance(el, Tile):
                el.do_layout()
            else:
                el.pack(self.layout_options())

    def layout_options(self):
        return {"side": "left", "pady": 5, "padx": 5}

    def pref(self, name, defval=None):
        v = self._kwargs.setdefault(name, defval)
        return v

    def set_pref(self, name, val):
        self._kwargs[name] = val

    def pref_int(self, name, defval):
        return int(self._kwargs.get(name, defval))

    def pref_float(self, name, defval):
        return float(self._kwargs.get(name, defval))

    def get_caption(self):
        return self.pref(
            "caption", self.pref("text", "... caption not-set" + str(self))
        )


class TileLabel(Tile):
    def create_element(self, frame):
        self._lbl = ttk.Label(frame, text=self.get_caption())
        return self._lbl


class TileLabelClick(TileLabel):
    def create_element(self, frame):
        lbl = super().create_element(frame)
        lbl.config(foreground="blue")
        lbl.config(cursor="hand1")
        lbl.bind("<Button-1>", self._handler)
        return lbl

    def _handler(self, event):
        print("_handler")
        self.pref("on_click", self.on_click)()

    def on_click(self):
        print(self.__class__.__name__, "on_click")


class TileButton(Tile):
    def create_element(self, frame):
        self._button = ttk.Button(
            frame,
            text=self.pref("commandtext", "..."),
            command=self.pref("command", self._handler),
        )
        return self._button

    def _handler(self):
        self.pref("on_click", self.on_click)()

    def on_click(self):
        print(self.__class__.__name__, "on_click")


class TileLabelButton(Tile):
    def create_element(self, frame):
        self._lbl = ttk.Label(frame, text=self.get_caption())
        self._button = ttk.Button(
            frame,
            text=self.pref("commandtext", "..."),
            command=self.pref("command", self._handler),
        )
        return [self._lbl, self._button]

    def _handler(self):
        self.pref("on_click", self.on_click)()

    def on_click(self):
        print(self.__class__.__name__, "on_click")


class TileEntry(Tile):
    def create_element(self, frame):
        self._lbl = ttk.Label(frame, text=self.get_caption())
        self._var = self._create_var()
        self._entry = self._create_entry(frame)
        return [self._lbl, self._entry]

    def _create_var(self):
        return StringVar()

    def _create_entry(self, frame):
        return ttk.Entry(frame, textvariable=self._var)

    def get_val(self):
        return self._var.get()

    def set_val(self, val=None):
        self._var.set(val)

    def validate(self):
        pass


class TileEntryButton(TileEntry):
    def create_element(self, frame):

        vars = super().create_element(frame)
        self._button = ttk.Button(
            frame,
            text=self.pref("commandtext", "..."),
            command=self.pref("command", self._handler),
        )

        vars.append(self._button)

        return vars

    def _handler(self):
        self.pref("on_click", self.on_click)()

    def on_click(self):
        print(self.__class__.__name__, "on_click", self.get_val())


class TileEntryCombo(TileEntry):
    def create_element(self, frame):

        vars = super().create_element(frame)

        self._values = list(self.pref("values", []))

        mf = self.pref("map_value", lambda x: x)
        self._map_values = list(map(mf, self._values))
        self._combo["values"] = self._map_values

        sel_idx = self.pref("sel_idx", None)
        if sel_idx != None:
            print("sel_idx", sel_idx)
            self.set_index(sel_idx)

        return vars

    def _create_entry(self, frame):
        self._combo = ttk.Combobox(frame, textvariable=self._var)
        self._combo.bind("<<ComboboxSelected>>", self._handler)
        return self._combo

    def _handler(self, event):
        self.pref("on_select", self.on_select)()

    def on_select(self):
        print(self.__class__.__name__, "on_select", self.get_select())

    def get_index(self):
        return self._combo.current()

    def set_index(self, pos):
        self._combo.current(pos)

    def get_values(self):
        return self._combo["values"]

    def get_select(self):
        idx = self.get_index()
        if idx < 0:
            return
        return self._values[idx]


class TileEntryListbox(TileEntry):
    def __init__internal__(self):
        super().__init__internal__()
        self.scrollbar()

        self._auto_scrollb = int(self.pref("max_show", 5))
        self._values = list(self.pref("values", []))

    def scrollbar(self, enable=True):
        self._scrollable = enable
        return self

    def set_values(self, values):
        self._values = values
        self._scroll_height()

    def _do_map(self, values):
        mf = self.pref("map_value", lambda x: f"{x} > {x}")
        self._map_values = list(map(mf, values))
        self._var.set(self._map_values)
        self._values = values

    def create_element(self, frame):

        vars = super().create_element(frame)

        self._do_map(self._values)

        print("self._scrollable", self._scrollable)

        if self._scrollable == True:
            self._scrollb = ttk.Scrollbar(
                frame,
                orient=VERTICAL,
                command=self._listb.yview,
            )
            self._listb.configure(yscrollcommand=self._scrollb.set)
            return [*vars, self._scrollb]

        self._listb.selection_set(0)

        return vars

    def _do_layout(self):
        super()._do_layout()
        self._listb.pack(padx=0)
        if self._scrollable:
            self._scrollb.pack(fill="y", padx=0)

    def _scroll_height(self):
        self.scrollbar()
        h = len(self._values)
        if h > self._auto_scrollb:
            h = self._auto_scrollb
        else:
            self.scrollbar(False)
        return h

    def _create_entry(self, frame):

        h = self._scroll_height()

        self._listb = Listbox(
            frame, listvariable=self._var, exportselection=False, height=h
        )
        self._listb.bind("<<ListboxSelect>>", self._handler)
        return self._listb

    def _handler(self, event):
        self.pref("on_select", self.on_select)()

    def on_select(self):
        print(self.__class__.__name__, "on_select", self.get_val())

    def get_val(self):
        idx = self._listb.curselection()  # no range
        idx = idx[0]
        return (idx, self._values[idx])

    def set_val(self, idx):
        # untested
        self._listb.selection_set(idx)


class TileEntrySpinbox(TileEntry):
    def create_element(self, frame):

        vars = super().create_element(frame)

        self._values = list(self.pref("values", []))
        mf = self.pref("map_value", lambda x: f"{x} > {x}")
        self._map_values = list(map(mf, self._values))

        _spin_opts = self.pref("spin_opts", {})
        _spin_opts["values"] = self._map_values

        self._spinb.config(**_spin_opts)

        return vars

    def _create_entry(self, frame):
        self._spinb = ttk.Spinbox(frame, textvariable=self._var)
        self._spinb.bind("<<Increment>>", self._handler)
        self._spinb.bind("<<Decrement>>", self._handler)
        return self._spinb

    def _handler(self, event):
        self.pref("on_change", self.on_change)()

    def on_change(self):
        print(self.__class__.__name__, "on_change", self.get_index(), self.get_val())

    def get_index(self):
        return self._map_values.index(self.get_val())

    def get_val(self):
        return self._spinb.get()

    def set_val(self, val):
        self._spinb.set(val)


class TileFileSelect(TileEntryButton):

    PATH = "path"
    """path: always add os.sep at the end"""

    def create_element(self, frame):
        vars = super().create_element(frame)

        self._filetypes = self.pref("filetypes", self.file_types())

        path = self.pref(self.PATH, self.get_base())
        self.set_val(self.fullpath(path))

        return vars

    def on_click(self):

        print("on_click")

        basedir = os.path.dirname(self.get_val())

        file = filedialog.askopenfilename(
            initialdir=basedir, title=self.get_caption(), filetypes=self._filetypes
        )

        if file:
            self.set_val(file)

    def get_base(self):
        return os.getcwdb()

    def file_types(self):
        return [("all files", "*.*")]

    def fullpath(self, path):
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        return path


class TileRows(Tile):
    def create_element(self, frame):
        vars = []
        for el in self.pref("source", []):
            if el == None:
                continue
            el.set_parent(self.frame)
            el.layout()
            vars.append(el)
        self._elem = vars
        return []

    def layout(self):
        super().layout()

    def _do_layout(self):
        super()._do_layout()

    def layout_options(self):
        super().layout_options()


class TileTab(Tile):
    def create_element(self, frame):

        self._tab = ttk.Notebook(frame)
        self._elem = []

        for el in self.pref("source", []):
            caption = ""
            if type(el) == tuple:
                caption = el[0]
                el = el[1]

            el.set_parent(self.frame)
            el.layout()

            self._elem.append(el)
            self._tab.add(el.frame, text=caption)

            self._tab_sel = 0

        self._tab.bind("<<NotebookTabChanged>>", self._handler)
        return self._tab

    def _handler(self, event):
        cur = self.get_index()
        if cur == self._tab_sel:
            return
        self._tab_sel = cur
        self.pref("on_change", self.on_change)()

    def on_change(self):
        print(self.__class__.__name__, "on_change", self.get_index())

    def get_index(self):
        return self._tab.index(self._tab.select())
