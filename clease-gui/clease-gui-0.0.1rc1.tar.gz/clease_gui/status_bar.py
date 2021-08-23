from collections import namedtuple
from contextlib import contextmanager
import functools
import ipywidgets as widgets
from IPython.display import display

from clease_gui import BaseDashboard, Colors

__all__ = ['StatusBar', 'update_statusbar']

UpdatableWidget = namedtuple('UpdatableWidget', 'widget, update_function')

# _bool2text = {True: u'\N{GREEN CHECK MARK}', False: u'\N{CROSS MARK}'}
_bool2text = {True: u'\u2705', False: u'\N{CROSS MARK}'}


def update_statusbar(func):
    """Decorator to update statusbar after function completion, and mark
    status as busy from a dashboard object. """
    @functools.wraps(func)
    def _wrapper(self, *args, **kwargs):
        # statusbar = display_ui.main_dashboard.status_bar
        try:
            statusbar = self.app_data[self.KEYS.STATUS]['statusbar']
        except KeyError:
            # Something happened, we couldn't get the statusbar
            return func(self, *args, **kwargs)

        # Set statusbar as busy
        with statusbar.status_busy():
            return_val = func(self, *args, **kwargs)
        return return_val

    return _wrapper


class StatusBar(BaseDashboard):
    def __init__(self, *args, **kwargs):
        self._processes = 0
        self.all_widgets = []
        super().__init__(*args, **kwargs)
        # Register this statusbar in the app data
        # So others can register it as busy
        self.app_data[self.KEYS.STATUS] = {'statusbar': self}

    def initialize(self):
        # Create widgets
        self.status_widget = widgets.HTML(value=self.is_busy_str())
        self.register_status_widget(self.status_widget, self.is_busy_str)

        self.has_settings_wdgt = widgets.Label(value=self.has_settings())
        self.register_status_widget(self.has_settings_wdgt, self.has_settings)

        self.has_eci_wdgt = widgets.Label(value=self.has_eci())
        self.register_status_widget(self.has_eci_wdgt, self.has_eci)

        self.has_supercell_widget = widgets.Label(value=self.has_supercell())
        self.register_status_widget(self.has_supercell_widget,
                                    self.has_supercell)

    def display(self):
        hbox1 = widgets.VBox(
            children=[
                self.status_widget,
                self.has_settings_wdgt,
            ],
            # Add a bit of margin to the right
            layout=widgets.Layout(margin='0 50px 0 0'),
        )

        hbox2 = widgets.VBox(children=[
            self.has_eci_wdgt,
            self.has_supercell_widget,
        ])

        boxes = widgets.HBox(children=[hbox1, hbox2],
                             layout=widgets.Layout(border='solid 1px'))

        display(boxes)

    def register_status_widget(self, widget, func):
        updatable = UpdatableWidget(widget, func)
        self.all_widgets.append(updatable)

    @property
    def processes(self):
        return self._processes

    def has_supercell(self):
        val = self.KEYS.SUPERCELL in self.app_data
        return self._format_bool('Supercell available?', val)

    def is_busy(self):
        return self.processes > 0

    def is_busy_str(self):
        s = 'Status:   '
        if self.is_busy() > 0:
            # status = Colors.latex_red('Busy')
            status = Colors.html_color('Busy', 'red')
        else:
            status = Colors.html_color('Idle', 'green')
        return f'{s} {status}'

    def has_settings(self):
        # return 'settings' in self.app_data
        val = self.KEYS.SETTINGS in self.app_data
        return self._format_bool('Settings available?', val)

    def has_eci(self):
        val = self.KEYS.ECI in self.app_data
        return self._format_bool('ECI available?', val)

    def _format_bool(self, s, boolean):
        val = _bool2text[boolean]
        return f'{s}   {val}'

    def update(self):
        for updatable_widget in self.all_widgets:
            func = updatable_widget.update_function
            updatable_widget.widget.value = func()

    @contextmanager
    def status_busy(self):
        try:
            self._processes += 1
            self.update()
            yield
        finally:
            self._processes -= 1
            self.update()

    def __repr__(self):
        return f'{self.__class__.__name__}(busy={self.is_busy()}, processes={self.processes})'
