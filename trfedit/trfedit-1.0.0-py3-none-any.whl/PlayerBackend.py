from gi.repository import Gtk
from trf import Player

from .GamesDialog import GamesDialog
from .TreeView import TextColumn
from .TreeViewPage import TreeViewPageBackend, TreeViewPage


class PlayerBackend(TreeViewPageBackend):
    def __init__(self, win):
        super().__init__(Gtk.ListStore(int, str, str, str, int,
                                       str, int, str, str, int), [
            TextColumn('Start Rank'),
            TextColumn('Name', self.on_name_changed),
            TextColumn('Sex', self.on_sex_changed),
            TextColumn('Title', self.on_title_changed),
            TextColumn('Rating', self.on_rating_changed),
            TextColumn('Federation', self.on_fed_changed),
            TextColumn('ID', self.on_id_changed),
            TextColumn('Date of Birth', self.on_birthdate_changed),
            TextColumn('Points', self.on_points_changed),
            TextColumn('Rank', self.on_rank_changed)
        ])
        self.win = win

    def on_name_changed(self, widget, path, text):
        if self.check_text_len(text, 33):
            index = int(path)
            self.tournament.players[index].name = text
            self.store[path][1] = text
            self.win.on_unsaved_changes()

    def on_sex_changed(self, widget, path, text):
        if self.check_text_len(text, 1):
            self.tournament.players[int(path)].sex = text
            self.store[path][2] = text
            self.win.on_unsaved_changes()

    def on_title_changed(self, widget, path, text):
        if self.check_text_len(text, 3):
            self.tournament.players[int(path)].title = text
            self.store[path][3] = text
            self.win.on_unsaved_changes()

    def on_rating_changed(self, widget, path, text):
        rating = self.parse_int(text, 9999)
        if rating is not None:
            self.tournament.players[int(path)].rating = rating
            self.store[path][4] = rating
            self.win.on_unsaved_changes()

    def parse_int(self, text, bound=2147483647):
        if not text.isdigit():
            self.win.show_error_dialog(
                'Could not parse number',
                'Input may only contain digits from 0 to 9')
            return None

        num = int(text)

        if num > bound:
            self.win.show_error_dialog(
                'Number out of range',
                f'Input must be less then or equal to {bound}')
            return None

        return num

    def on_fed_changed(self, widget, path, text):
        if self.check_text_len(text, 3):
            self.tournament.players[int(path)].fed = text
            self.store[path][5] = text
            self.win.on_unsaved_changes()

    def check_text_len(self, text, limit):
        if len(text) > limit:
            self.win.show_error_dialog(
                'Input to long',
                f'The input may only be {limit} characters long')
            return False
        return True

    def on_id_changed(self, widget, path, text):
        id = self.parse_int(text)
        if id is not None:
            self.tournament.players[int(path)].id = id
            self.store[path][6] = id
            self.win.on_unsaved_changes()

    def on_birthdate_changed(self, widget, path, text):
        if self.check_text_len(text, 10):
            self.tournament.players[int(path)].birthdate = text
            self.store[path][7] = text
            self.win.on_unsaved_changes()

    def on_points_changed(self, widget, path, text):
        try:
            points = float(text)
        except ValueError as e:
            self.win.show_error_dialog('Cannot parse number', str(e))
            return

        if points < 0 or points % 0.5 != 0:
            self.win.show_error_dialog(
                'Invalid number of points',
                'Points must be a nonnegative whole multiple of 0.5')
            return

        if points >= 100:
            self.win.show_error_dialog(
                'Invalid number of points',
                'Points must be less than 100')
            return

        self.tournament.players[int(path)].points = points
        self.store[path][8] = self.format_points(points)
        self.win.on_unsaved_changes()

    def format_points(self, points):
        return format(points, '.1f')

    def on_rank_changed(self, widget, path, text):
        rank = self.parse_int(text, 9999)
        if rank is not None:
            self.tournament.players[int(path)].rank = rank
            self.store[path][9] = rank
            self.win.on_unsaved_changes()

    def append_new_row(self):
        index = len(self.tournament.players)

        player = Player(name='New player', startrank=index+1)
        self.append_player_to_store(player)

        self.tournament.players.append(player)
        self.update_numplayers()

        return index

    def append_player_to_store(self, player):
        self.store.append([
            player.startrank,
            player.name,
            player.sex,
            player.title,
            player.rating,
            player.fed,
            player.id,
            player.birthdate,
            self.format_points(player.points),
            player.rank
        ])

    def swap_rows(self, i1, i2):
        a = self.tournament.players[i1]
        b = self.tournament.players[i2]

        self.tournament.players[i1] = b
        self.tournament.players[i2] = a

        # TODO: Fix startranks in teams
        for player in self.tournament.players:
            for game in player.games:
                if game.startrank == a.startrank:
                    game.startrank = b.startrank
                elif game.startrank == b.startrank:
                    game.startrank = a.startrank

        t = a.startrank
        a.startrank = b.startrank
        b.startrank = t

        self.swap_store_rows(i1, i2)
        self.store[i1][0] = b.startrank
        self.store[i2][0] = a.startrank

    def remove_row_from_data(self, index):
        startrank = self.tournament.players[index].startrank

        for i, player in enumerate(self.tournament.players):
            player.games = list(filter(lambda g: g.startrank != startrank,
                                       player.games))
            for game in player.games:
                if game.startrank > startrank:
                    game.startrank -= 1

            if player.startrank > startrank:
                player.startrank -= 1
                self.store[i][0] = player.startrank

        del self.tournament.players[index]
        self.update_numplayers()

    def __len__(self):
        return len(self.tournament.players)

    def set_tournament(self, tournament):
        self.tournament = tournament

        self.store.clear()
        for player in tournament.players:
            self.append_player_to_store(player)

    def update_numplayers(self):
        self.tournament.numplayers = len(self.tournament.players)
        self.tournament.numplayers = len(filter(
            lambda p: p.rating is not None and p.rating > 0,
            self.tournament.players))


class PlayerPage(TreeViewPage):
    def __init__(self, win):
        super().__init__(win, PlayerBackend(win))

        games_button = Gtk.Button.new_with_mnemonic('Games')
        games_button.connect('clicked', self.on_games)
        self.action_bar.add(games_button)

    def on_games(self, widget):
        index = self.get_selected_row()
        if index is not None:
            dialog = GamesDialog(self.win, index)
            dialog.run()
            dialog.destroy()
