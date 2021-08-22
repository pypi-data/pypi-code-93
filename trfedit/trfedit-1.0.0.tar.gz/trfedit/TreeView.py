from abc import ABC, abstractmethod
from gi.repository import Gtk


class TreeViewBackend(ABC):
    def __init__(self, store, columns):
        self.store = store
        self.columns = columns

    @abstractmethod
    def append_new_row(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    def remove_row(self, index):
        iter = self.iter_for_row(index)
        self.remove_row_from_data(index)
        self.store.remove(iter)

    def iter_for_row(self, index):
        return self.store[index].iter


class TreeViewColumn(ABC):
    def __init__(self, title, on_changed=None):
        self.title = title
        self.on_changed = on_changed

    @abstractmethod
    def get_renderer(self):
        pass


class TextColumn(TreeViewColumn):
    def __init__(self, title, on_changed=None):
        super().__init__(title, on_changed)

    def get_renderer(self):
        renderer = Gtk.CellRendererText()

        if self.on_changed is not None:
            renderer.set_property('editable', True)
            renderer.connect('edited', self.on_changed)

        return renderer


class ComboColumn(TreeViewColumn):
    def __init__(self, title, store, on_changed):
        super().__init__(title, on_changed)
        self.store = store

    def get_renderer(self):
        renderer = Gtk.CellRendererCombo()

        renderer.set_property('model', self.store)
        renderer.set_property('text-column', 1)
        renderer.set_property('has-entry', False)

        renderer.set_property('editable', True)
        renderer.connect('changed', self.on_changed)

        return renderer


class TreeView(Gtk.Box):
    def __init__(self, win, backend):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.backend = backend

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_vexpand(True)

        self.treeview = Gtk.TreeView(model=self.backend.store)

        for i, column in enumerate(self.backend.columns):
            column = Gtk.TreeViewColumn(column.title, column.get_renderer(), text=i)
            self.treeview.append_column(column)

        self.scroll.add(self.treeview)
        self.pack_start(self.scroll, True, True, 0)

        self.action_bar = Gtk.ActionBar()

        new_button = Gtk.Button.new_from_stock(Gtk.STOCK_ADD)
        new_button.connect('clicked', self.on_new)
        self.action_bar.add(new_button)

        self.pack_start(self.action_bar, False, False, 0)

    def on_new(self, widget):
        index = self.backend.append_new_row()
        self.treeview.set_cursor(index)
        self.win.on_unsaved_changes()

    def get_selected_row(self):
        path, _ = self.treeview.get_cursor()
        if path is None:
            return None
        return path.get_indices()[0]
