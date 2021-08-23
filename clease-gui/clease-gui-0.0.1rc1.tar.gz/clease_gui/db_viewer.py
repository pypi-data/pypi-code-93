import logging
from IPython.display import display, clear_output
import ipywidgets as widgets
import ase.visualize
import pandas as pd

from clease_gui import BaseDashboard, update_statusbar
import clease_gui as gui

__all__ = ['DBViewerDashboard']

logger = logging.getLogger(__name__)
gui.register_logger(logger)


class DBViewerDashboard(BaseDashboard):
    def initialize(self):

        self.db_select_widget = widgets.Text(description='DB name:', value='')
        db_name_help = widgets.Label(('Leave empty to use database specified '
                                      'in the settings object.'))
        self.db_select_box = widgets.HBox(
            children=[self.db_select_widget, db_name_help])

        self.selection_parameters_widget = widgets.Text(
            description='Selection:', value='')

        selection_help_label = widgets.Label(
            ('For more information on querying, see '
             'https://wiki.fysik.dtu.dk/ase/ase/db/db.html#querying'))
        self.selection_box = widgets.HBox(
            children=[self.selection_parameters_widget, selection_help_label])

        self.draw_selection_button = widgets.Button(
            description='Open in ASE GUI')
        self.draw_selection_button.on_click(self._on_draw_selection_click)

        self.print_db_button = widgets.Button(description='Show DB content')
        self.print_db_button.on_click(self._on_print_db)

        # Output for displaying the ASE database as a pandas DF
        self.db_content_out = widgets.Output(layout=dict(
            overflow='auto',
            width='100%',
            height='350px',
        ))

    @gui.update_statusbar
    @gui.utils.disable_cls_widget('print_db_button')
    def _on_print_db(self, b):
        try:
            self._print_db()
        except Exception as exc:
            logger.error(exc)

    def _print_db(self):
        db_name = str(self.db_name)
        selection = self.selection_parameters_widget.value
        con = self.get_connection()
        out = self.db_content_out
        logger.info('Querying database %s', db_name)

        rows = con.select(selection)
        df = ase_db_rows_to_df(rows)
        with out:
            clear_output(wait=True)
            with pd.option_context('display.max_rows', None,
                                   'display.max_columns', None):
                # Temporarily set display context to all of the rows
                # and columns we have.
                # We don't wanna truncate here.
                display(df)

    def display(self):
        buttons = widgets.HBox(children=[
            self.print_db_button,
            self.draw_selection_button,
        ])
        display(
            self.db_select_box,
            self.selection_box,
            buttons,
            self.db_content_out,
        )

    @property
    def db_name(self):
        value = self.db_select_widget.value
        if value == '':
            # Use DB name from settings
            return self.get_db_name()
        return self.app_data[self.KEYS.CWD] / value

    @property
    def settings(self):
        return self.app_data[self.KEYS.SETTINGS]

    def get_connection(self):
        return ase.db.connect(self.db_name)

    def get_selection_parameters(self):
        value = self.selection_parameters_widget.value
        if value == '':
            return None
        return value

    def get_selection(self):
        selection = self.get_selection_parameters()
        con = self.get_connection()

        return [row.toatoms() for row in con.select(selection=selection)]

    @update_statusbar
    def _on_draw_selection_click(self, b):
        self._draw_selection()

    def _draw_selection(self):
        images = self.get_selection()
        ase.visualize.view(images)


def ase_db_rows_to_df(rows) -> pd.DataFrame:
    """Convert an ASE database into a pandas data frame"""
    rows = list(rows)
    base_keys = [
        'id', 'formula', 'calculator', 'energy', 'natoms', 'pbc', 'volume',
        'charge', 'mass'
    ]

    # Grab all extra keys in the key_value_pairs
    extra_keys = []
    for row in rows:
        keys = row.key_value_pairs.keys()
        for key in keys:
            if key not in extra_keys:
                extra_keys.append(key)

    all_keys = base_keys + extra_keys
    # Now populate the data
    rows_list = []
    for row in rows:
        data = {}
        for key in base_keys:
            try:
                value = getattr(row, key)
            except AttributeError:
                value = None
            data[key] = _formatter(key, value)
        kvp_dct = row.key_value_pairs
        for key in extra_keys:
            value = kvp_dct.get(key, None)
            data[key] = _formatter(key, value)
        rows_list.append(data)
    return pd.DataFrame(rows_list, columns=all_keys)


def _formatter(key, value):
    """Helper function to format the value, possibly
    on the basis of the name of the key"""
    if value is None:
        value = '-'
    if key == 'pbc':
        # Convert [True, True, True] => 'TTT'
        # or [True, False, False] => 'TFF'
        value = ''.join([str(v)[0] for v in value])

    return value
