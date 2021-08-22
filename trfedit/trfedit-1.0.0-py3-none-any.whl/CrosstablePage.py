from gi.repository import Gtk, Gdk


RESULT_BY_KEY = {
    Gdk.KEY_1: '1',
    Gdk.KEY_0: '0',
    Gdk.KEY_2: '=',
}


class CrosstablePage(Gtk.Box):
    def __init__(self, win):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.tournament = None

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_hexpand(True)
        self.scroll.set_vexpand(True)

        self.pack_start(self.scroll, True, True, 0)

        self.grid = Gtk.Grid.new()
        self.grid.set_column_spacing(5)
        self.grid.set_row_spacing(5)
        self.scroll.add(self.grid)

        self.grid.attach(self.make_header_label('#'), 0, 0, 1, 2)
        self.grid.attach(self.make_header_label('Name'), 1, 0, 1, 2)

        self.first_crosstable_row = 2
        self.first_crosstable_column = 2

    def make_header_label(self, header):
        label = Gtk.Label()
        label.set_markup(f'<big><b>{header}</b></big>')
        return label

    def set_name(self, index, name):
        label = self.grid.get_child_at(1, index + self.first_crosstable_row)
        label.set_text(name)

    def generate_crosstable_cells(self):
        while self.grid.get_child_at(0, self.first_crosstable_row) is not None:
            self.grid.remove_row(self.first_crosstable_row)

        while self.grid.get_child_at(self.first_crosstable_column, 0) is not None:
            self.grid.remove_column(self.first_crosstable_row)

        for i, player in enumerate(self.tournament.players):
            label = Gtk.Label(label=str(player.startrank))
            label.set_xalign(1)
            self.grid.attach(label, 0, i+self.first_crosstable_row, 1, 1)

            label = Gtk.Label(label=str(player.startrank))
            label.set_xalign(0.5)
            self.grid.attach(label, 2*i + self.first_crosstable_column, 0, 2, 1)

            label = Gtk.Label(label=player.name)
            label.set_xalign(0)
            self.grid.attach(label, 1, i + self.first_crosstable_row, 1, 1)

            for j, other in enumerate(self.tournament.players):
                if i == j:
                    label = Gtk.Label(label='XXXXX')
                    self.grid.attach(label, 2*i + self.first_crosstable_column, j + self.first_crosstable_row, 2, 1)
                else:
                    color_entry = Gtk.Entry()
                    color_entry.connect('key-press-event', self.create_on_color_pressed(i, j))
                    color_entry.set_width_chars(1)
                    self.grid.attach(color_entry, 2*i + self.first_crosstable_column, j + self.first_crosstable_row, 1, 1)

                    result_entry = Gtk.Entry()
                    result_entry.connect('key-press-event', self.create_on_result_pressed(i, j))
                    result_entry.set_width_chars(1)
                    self.grid.attach(result_entry, 2*i + self.first_crosstable_column + 1, j + self.first_crosstable_row, 1, 1)

                    game = next(filter(lambda g: g.startrank == other.startrank, player.games), None)
                    if game is not None:
                        color_entry.set_text(game.color)
                        result_entry.set_text(game.result)

        self.grid.show_all()

    def create_on_result_pressed(self, row, column):
        def on_result_pressed(widget, event):
            result = RESULT_BY_KEY.get(event.keyval)
            widget.set_text(result or '')

        return on_result_pressed

    def create_on_color_pressed(self, row, column):
        def on_color_pressed(widget, event):
            print('color', row, column, widget, event)

        return on_color_pressed

    def set_tournament(self, tournament):
        self.tournament = tournament
        self.generate_crosstable_cells()
