from gi.repository import Gtk

import datetime
import re

from .TreeView import TextColumn
from .TreeViewPage import TreeViewPageBackend


DATE_FORMAT = '%y/%m/%d'


class RoundDatesBackend(TreeViewPageBackend):
    def __init__(self, win):
        super().__init__(Gtk.ListStore(int, str), [
            TextColumn('Round', None),
            TextColumn('Date', self.on_date_changed)
        ])
        self.win = win

    def append_new_row(self):
        round = len(self.tournament.rounddates)
        today = datetime.date.today().strftime(DATE_FORMAT)

        self.store.append([round+1, today])
        self.tournament.rounddates.append(today)

        return round

    def swap_rows(self, i1, i2):
        a = self.tournament.rounddates[i1]
        b = self.tournament.rounddates[i2]

        self.tournament.rounddates[i1] = b
        self.tournament.rounddates[i2] = a

        self.store[i1][1] = b
        self.store[i2][1] = a

    def on_date_changed(self, widget, path, text):
        if re.search('\\s+', text):
            self.win.show_error_dialog('Invalid round date',
                                       'No whitespace allowed in round dates')
            return

        self.tournament.rounddates[int(path)] = text
        self.store[path][1] = text
        self.win.on_unsaved_changes()

    def remove_row_from_data(self, index):
        del self.tournament.rounddates[index]

    def __len__(self):
        return len(self.tournament.rounddates)

    def set_tournament(self, tournament):
        self.tournament = tournament

        self.store.clear()
        for i, date in enumerate(tournament.rounddates):
            self.store.append([i+1, date])
