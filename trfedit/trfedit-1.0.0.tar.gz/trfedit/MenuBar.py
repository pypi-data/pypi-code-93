from abc import ABC, abstractmethod
from gi.repository import Gtk


class MenuItem(ABC):
    def __init__(self, callback=None, accelerator=None):
        self.callback = callback
        self.accelerator = accelerator

    @abstractmethod
    def new_menu_item(self):
        pass

    def make_menu_item(self, agr):
        item = self.new_menu_item()

        if self.callback is not None:
            item.connect('activate', self.callback)

        if self.accelerator is not None:
            key, mod = Gtk.accelerator_parse(self.accelerator)
            item.add_accelerator('activate', agr,
                                 key, mod,
                                 Gtk.AccelFlags.VISIBLE)

        return item


class StockMenuItem(MenuItem):
    def __init__(self, stock_id, callback, accelerator=None):
        super().__init__(callback, accelerator)
        self.stock_id = stock_id

    def new_menu_item(self):
        return Gtk.ImageMenuItem.new_from_stock(self.stock_id)


class LabeledMenuItem(MenuItem):
    def __init__(self, label, callback, accelerator=None):
        super().__init__(callback, accelerator)
        self.label = label

    def new_menu_item(self):
        return Gtk.MenuItem.new_with_label(self.label)


class SeperatorMenuItem(MenuItem):
    def __init__(self):
        super().__init__(None, None)

    def new_menu_item(self):
        return Gtk.SeparatorMenuItem.new()


class MenuBar(Gtk.MenuBar):
    def __init__(self):
        super().__init__()
        self.agr = Gtk.AccelGroup()

    def add_menu(self, label, items):
        submenu = Gtk.Menu()
        menu = Gtk.MenuItem.new_with_mnemonic(label)
        menu.set_submenu(submenu)

        for item in items:
            submenu.append(item.make_menu_item(self.agr))

        self.append(menu)
