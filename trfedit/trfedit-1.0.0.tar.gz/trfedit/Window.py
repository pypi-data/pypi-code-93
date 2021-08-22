from gi.repository import Gtk
import traceback
import trf

from .MenuBar import MenuBar, StockMenuItem, SeperatorMenuItem, LabeledMenuItem
from .PlayerBackend import PlayerPage
from .RoundDatesBackend import RoundDatesBackend
from .TournamentPage import TournamentPage
from .TreeViewPage import TreeViewPage
from .XXFieldsBackend import XXFieldsBackend


class Window(Gtk.Window):
    def __init__(self):
        super().__init__(title='trfedit')
        self.tournament = None
        self.tournament_path = None

        menu_bar = MenuBar()
        self.add_accel_group(menu_bar.agr)

        self.unsaved_changes = False

        self.notebook = Gtk.Notebook()

        self.tournament_page = TournamentPage(self.on_unsaved_changes)
        self.notebook.append_page(
            self.tournament_page,
            Gtk.Label(label='Tournament'))

        self.rounddates_backend = RoundDatesBackend(self)
        self.rounddates_page = TreeViewPage(self, self.rounddates_backend)
        self.notebook.append_page(
            self.rounddates_page,
            Gtk.Label(label='Round Dates'))

        self.xx_fields_backend = XXFieldsBackend(self)
        self.xx_fields_page = TreeViewPage(self, self.xx_fields_backend)
        self.notebook.append_page(
            self.xx_fields_page,
            Gtk.Label(label='XX Fields'))

        self.player_page = PlayerPage(self)
        self.notebook.append_page(
            self.player_page,
            Gtk.Label(label='Players'))

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(menu_bar, False, False, 0)
        vbox.pack_start(self.notebook, True, True, 0)

        self.add(vbox)

        self.connect('delete-event', self.on_quit)

        # TODO: teams: List[str] = field(default_factory=list)

        menu_bar.add_menu('_File', [
            StockMenuItem(Gtk.STOCK_NEW,     self.on_file_new,        '<Control>N'),
            StockMenuItem(Gtk.STOCK_OPEN,    self.on_file_open,       '<Control>O'),
            StockMenuItem(Gtk.STOCK_SAVE,    self.on_file_save,       '<Control>S'),
            StockMenuItem(Gtk.STOCK_SAVE_AS, self.on_file_save_as,    '<Shift><Control>S'),
            SeperatorMenuItem(),
            StockMenuItem(Gtk.STOCK_QUIT,    self.on_quit,            '<Control>Q')
        ])

        menu_bar.add_menu(
            'Round Dates',
            self.make_page_menu('round date', self.rounddates_page, '<Control>R'))

        menu_bar.add_menu(
            'XX Fields',
            self.make_page_menu('xx field', self.xx_fields_page, '<Control>X'))

        menu_bar.add_menu(
            'Players',
            self.make_page_menu('player', self.player_page, '<Control>P')
            + self.make_games_menu())

        menu_bar.add_menu('_Help', [
            StockMenuItem(Gtk.STOCK_INFO, self.on_info)
        ])

    def on_info(self, widget):
        dialog = Gtk.AboutDialog.new()
        dialog.set_program_name('trfedit')
        dialog.set_authors(['Oshgnacknak'])
        dialog.set_website('https://github.com/sklangen/trfedit')
        dialog.set_license_type(Gtk.License.GPL_3_0)

        dialog.run()
        dialog.destroy()

    def make_games_menu(self):
        def on_games(widget):
            if self.is_page_focused(self.player_page):
                self.player_page.on_games(widget)

        return [
            LabeledMenuItem('Edit games', on_games, '<Control>G')
        ]

    def make_page_menu(self, element_name, page, new_accelerator):
        def on_new(widget):
            self.focus_page(page)
            page.on_new(widget)

        def on_remove(widget):
            if self.is_page_focused(page):
                page.on_remove(widget)

        def on_up(widget):
            if self.is_page_focused(page):
                page.on_up(widget)

        def on_down(widget):
            if self.is_page_focused(page):
                page.on_down(widget)

        return [
            LabeledMenuItem(f'New {element_name}',       on_new, new_accelerator),
            LabeledMenuItem(f'Remove {element_name}',    on_remove),
            LabeledMenuItem(f'Move {element_name} up',   on_up),
            LabeledMenuItem(f'Move {element_name} down', on_down)
        ]

    def is_page_focused(self, page):
        return self.notebook.page_num(page) == self.notebook.get_current_page()

    def focus_page(self, page):
        self.notebook.set_current_page(self.notebook.page_num(page))

    def on_file_new(self, widget):
        self.ensure_changes_saved()

        path = self.ask_for_tournament_path(Gtk.STOCK_NEW)
        if path is not None:
            self.tournament_path = path
            self.set_tournament_to_new_tournament()
            self.update_title()

    def ensure_changes_saved(self):
        while self.unsaved_changes:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.YES_NO,
                text='Unsaved changes may be lost')

            dialog.format_secondary_text(
                'Do you want to save before exiting?')

            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                self.save_tournament(self.tournament_path)
            else:
                self.on_saved_changes()

            dialog.destroy()

    def update_title(self):
        title = 'trfedit'

        if self.tournament_path is not None:
            title = self.tournament_path + ' - ' + title

        if self.unsaved_changes:
            title = '*' + title

        self.set_title(title)

    def on_file_open(self, widget):
        self.ensure_changes_saved()

        path = self.ask_for_tournament_path(Gtk.STOCK_OPEN)
        if path is not None:
            self.set_tournament_by_path(path)

    def on_file_save(self, widget):
        self.save_tournament(self.tournament_path)

    def on_file_save_as(self, widget):
        self.save_tournament(None)

    def save_tournament(self, path):
        if path is None:
            path = self.ask_for_tournament_path(Gtk.STOCK_SAVE)

        if path is None:
            return

        try:
            with open(path, 'w') as f:
                trf.dump(f, self.tournament)
        except Exception as e:
            self.show_error_dialog('Error writing tournament', str(e))
            traceback.print_exc()
            return

        self.tournament_path = path
        self.on_saved_changes()

    def on_saved_changes(self):
        self.unsaved_changes = False
        self.update_title()

    def ask_for_tournament_path(self, stock_id):
        path = None

        dialog = Gtk.FileChooserDialog(
            'Please choose a file', self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                stock_id, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()

        dialog.destroy()
        return path

    def show_error_dialog(self, title, secondary_text):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CANCEL,
            text=title)

        dialog.format_secondary_text(secondary_text)
        dialog.run()

        dialog.destroy()

    def on_unsaved_changes(self):
        self.unsaved_changes = True
        self.update_title()

    def on_quit(self, widget, event=None):
        self.quit()

    def quit(self):
        self.ensure_changes_saved()
        Gtk.main_quit()

    def set_tournament(self, tournament):
        self.tournament = tournament
        self.tournament_page.set_tournament(tournament)
        self.rounddates_backend.set_tournament(tournament)
        self.xx_fields_backend.set_tournament(tournament)
        self.player_page.backend.set_tournament(tournament)
        self.on_saved_changes()

    def set_tournament_to_new_tournament(self):
        self.tournament_path = None
        self.set_tournament(trf.Tournament(name='Unnamed Tournament'))

    def set_tournament_by_path(self, path):
        tour = None

        try:
            with open(path, 'r') as f:
                tour = trf.load(f)
        except Exception as e:
            self.show_error_dialog('Error reading tournament', str(e))
            traceback.print_exc()

            if self.tournament is None:
                self.set_tournament_to_new_tournament()

        if tour is not None:
            self.tournament_path = path
            self.set_tournament(tour)
