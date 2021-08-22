from gi.repository import Gtk

import re

from .TreeView import TextColumn
from .TreeViewPage import TreeViewPageBackend


XX_FIELD_PATTERN = re.compile('XX[\\w\\d-]+')


class XXFieldsBackend(TreeViewPageBackend):
    def __init__(self, win):
        super().__init__(Gtk.ListStore(str, str), [
            TextColumn('Name',  self.on_name_changed),
            TextColumn('Value', self.on_value_changed)
        ])
        self.win = win
        self.tournament = None

    def append_new_row(self):
        index = len(self.tournament.xx_fields)

        name = 'XX_new_field'
        if name in self.tournament.xx_fields:
            tries = 1
            othername = name
            while othername in self.tournament.xx_fields:
                othername = name + '_' + str(tries)
                tries += 1
            name = othername

        self.store.append([name, ''])
        self.tournament.xx_fields[name] = ''

        return index

    def swap_rows(self, i1, i2):
        self.swap_store_rows(i1, i2)

    def on_name_changed(self, widget, path, text):
        if not XX_FIELD_PATTERN.fullmatch(text):
            self.win.show_error_dialog('Invalid XX field name',
                                       'Must be "XX" folled by alphanumeric text without spaces')
            return

        oldname = self.store[path][0]
        if text == oldname:
            return

        if text in self.tournament.xx_fields:
            self.win.show_error_dialog('XX field name already in use',
                                       'XX field names must be unique')
            return

        self.tournament.xx_fields[text] = self.tournament.xx_fields[oldname]
        del self.tournament.xx_fields[oldname]

        self.store[path][0] = text
        self.win.on_unsaved_changes()

    def on_value_changed(self, widget, path, text):
        name = self.store[path][0]
        self.store[path][1] = text
        self.tournament.xx_fields[name] = text
        self.win.on_unsaved_changes()

    def remove_row_from_data(self, index):
        name = self.store[index][0]
        del self.tournament.xx_fields[name]

    def __len__(self):
        return len(self.tournament.xx_fields)

    def set_tournament(self, tournament):
        self.tournament = tournament

        self.store.clear()
        for name, value in tournament.xx_fields.items():
            self.store.append([name, value])
