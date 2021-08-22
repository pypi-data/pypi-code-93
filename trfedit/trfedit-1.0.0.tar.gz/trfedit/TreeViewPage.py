from abc import abstractmethod
from gi.repository import Gtk, Gdk

from .TreeView import TreeView, TreeViewBackend


class TreeViewPageBackend(TreeViewBackend):
    def __init__(self, store, columns):
        super().__init__(store, columns)

    @abstractmethod
    def remove_row_from_data(self, index):
        pass

    @abstractmethod
    def swap_rows(self, index):
        pass

    def swap_store_rows(self, i1, i2):
        self.store.swap(self.iter_for_row(i1), self.iter_for_row(i2))


class TreeViewPage(TreeView):
    def __init__(self, win, backend):
        super().__init__(win, backend)

        self.treeview.connect('key-press-event', self.on_key_typed)

        remove_button = Gtk.Button.new_from_stock(Gtk.STOCK_REMOVE)
        remove_button.connect('clicked', self.on_remove)
        self.action_bar.add(remove_button)

        up_button = Gtk.Button.new_from_stock(Gtk.STOCK_GO_UP)
        up_button.connect('clicked', self.on_up)
        self.action_bar.add(up_button)

        down_button = Gtk.Button.new_from_stock(Gtk.STOCK_GO_DOWN)
        down_button.connect('clicked', self.on_down)
        self.action_bar.add(down_button)

    def on_key_typed(self, widget, event):
        if event.keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace):
            self.remove_row()

    def on_remove(self, widget):
        self.remove_row()

    def remove_row(self):
        index = self.get_selected_row()
        if index is not None:
            self.backend.remove_row(index)
            self.win.on_unsaved_changes()

    def on_down(self, widget):
        self.move_row(+1)

    def on_up(self, widget):
        self.move_row(-1)

    def move_row(self, dir):
        index = self.get_selected_row()
        if index is not None:
            other = (index+dir) % len(self.backend)
            self.backend.swap_rows(index, other)

            self.treeview.set_cursor(other)
            self.win.on_unsaved_changes()
