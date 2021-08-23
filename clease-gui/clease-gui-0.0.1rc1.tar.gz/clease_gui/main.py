from pathlib import Path, PurePath
import logging
from collections import namedtuple
from IPython.display import display, clear_output
import ipywidgets as widgets
from clease_gui import (utils, BaseDashboard, save_app_data, load_app_data,
                        update_statusbar, AppDataKeys)
from .logging_widget import (default_handler, set_all_levels, register_logger,
                             initialize_clease_gui_logging)

__all__ = ['display_ui', 'MainDashboard', 'get_assets_path']

logger = logging.getLogger(__name__)
register_logger(logger)


class TestAppData(BaseDashboard):
    def initialize(self):
        self.test_button = widgets.Button(description='See app data')
        self.test_button.on_click(self._on_click)
        self.output = widgets.Output()

    def display(self):
        display(self.test_button, self.output)

    def _on_click(self, b):
        from pprint import pprint
        data = self.app_data.copy()
        if 'settings' in data:
            data['settings'] = data['settings'].todict()
        with self.output:
            clear_output(wait=True)
            pprint(data)


class MainDashboard(BaseDashboard):
    def initialize(self):
        # We need to delay the import of these packages, to break cyclic imports
        from .status_bar import StatusBar
        from .db_viewer import DBViewerDashboard
        from .settings_maker import SettingsMakerDashboard
        from .new_structures import NewStructureDashboard
        from .calculate import CalculateDashboard
        from .fitting import FittingDashboard
        from .supercell import SupercellDashboard
        from .montecarlo import MainMCDashboard

        # The status bar should be the first thing to be initialized,
        # since it adds itself to the app_data
        self.status_bar = StatusBar(self.app_data)
        self.status_output = widgets.Output()
        with self.status_output:
            clear_output()
            self.status_bar.display()

        Tab = namedtuple('Tab', 'output,name')
        tabs = []  # List containing the tab objects to be added
        self.dashboards = {}  # Store the dashboards for internal access

        def add_tab(dashboard, display_name):
            """Helper function to add new tabs to the main dashboard"""
            output = widgets.Output()
            # Create the dashboard
            board = dashboard(self.app_data)
            name = display_name.lower().replace(' ', '_')
            self.dashboards[name] = board
            with output:
                clear_output()
                board.display()

            tab = Tab(output, display_name)
            tabs.append(tab)

        # Add main tabs
        add_tab(SettingsMakerDashboard, 'Settings')
        add_tab(NewStructureDashboard, 'New Structures')
        add_tab(DBViewerDashboard, 'Inspect DB')
        add_tab(CalculateDashboard, 'Calculate')
        add_tab(FittingDashboard, 'ECI')
        add_tab(SupercellDashboard, 'Supercell')
        add_tab(MainMCDashboard, 'Monte Carlo')
        if self.dev_mode:
            add_tab(TestAppData, 'Testing')

        # Add the tabs to the main dashboard
        self.tab = widgets.Tab(children=[tab.output for tab in tabs])

        # Add current working directory widet in the top
        cwd = Path('.').resolve()
        self.cwd_widget = widgets.Text(
            value=str(cwd),
            description='Current working directory:',
            layout=widgets.Layout(height="auto", width="100%"),
            style={'description_width': 'initial'},
        )
        # Update the app data, and observe any changes
        self.set_cwd(self.cwd_widget.value)
        self.cwd_widget.observe(self._on_cwd_change)
        self.logo = _get_logo_widget()

        for ii, tab in enumerate(tabs):
            self.tab.set_title(ii, tab.name)

        # Add button to clear logs
        clear = widgets.Button(description='Clear Logs')
        log_level = widgets.Dropdown(
            options=[
                ('Error', logging.ERROR),
                ('Warning', logging.WARNING),
                ('Info', logging.INFO),
                ('Debug', logging.DEBUG),
            ],
            value=logging.INFO,
            description='Logging level:',
            style={'description_width': 'initial'},
        )

        def on_clear_click(b):
            default_handler.clear_logs()

        clear.on_click(on_clear_click)

        def on_log_level_change(change):
            if utils.is_value_change(change):
                set_all_levels(change['new'])

        log_level.observe(on_log_level_change)
        initialize_clease_gui_logging()

        self.log_box = widgets.HBox(children=[clear, log_level])

        # save/load app state button
        self.save_app_state_button = widgets.Button(
            description='Save app data')
        self.save_app_state_button.on_click(self._on_save_app_data)
        self.load_app_state_button = widgets.Button(
            description='Load app data')
        self.load_app_state_button.on_click(self._on_load_app_data)

    def display(self):
        # Top bar box with logo and CWD widget
        top_bar_box = widgets.HBox(children=[self.logo, self.cwd_widget],
                                   layout={'align_items': 'center'})
        display(top_bar_box)
        display(self.tab)
        display(self.status_output)
        default_handler.show_logs()
        display(self.log_box)
        app_data_state_buttons = widgets.HBox(
            children=[self.save_app_state_button, self.load_app_state_button])
        display(app_data_state_buttons)

    @property
    def cwd(self):
        return self.app_data[self.KEYS.CWD]

    def set_cwd(self, value):
        self.app_data[self.KEYS.CWD] = Path(value).resolve()

    def _on_cwd_change(self, change) -> Path:
        if utils.is_value_change(change):
            self.set_cwd(change.new)

    @property
    def app_data_file_name(self):
        # Hardcode app data filename for now.
        return self.cwd / '.clease_gui_app_data.json'

    @update_statusbar
    def _on_save_app_data(self, b):
        try:
            fname = self.app_data_file_name
            logger.info('Saving app data to file: %s', str(fname))
            self._save_app_data(fname)
            logger.info('Save complete.')
        except Exception as exc:
            self.log_error(logger, exc)

    def _save_app_data(self, filename):
        save_app_data(self.app_data, filename)

    def _load_app_data(self, filename):
        new_data = load_app_data(filename)
        # Get the supercell, and make the supercell dashboard set it
        supercell = self.app_data.pop(self.KEYS.SUPERCELL, None)
        if supercell is not None:
            logger.debug('Updating supercell from app data')
            dashboard = self.dashboards['supercell']
            dashboard.set_supercell(supercell)

        self.app_data.update(new_data)
        # Try to update the settings page
        settings = new_data.get(self.KEYS.SETTINGS, None)
        if settings is not None:
            settings_dashboard = self.dashboards['settings']
            settings_dashboard.set_settings_widget_states(settings)

    @update_statusbar
    def _on_load_app_data(self, b):
        try:
            fname = self.app_data_file_name
            logger.info('Loading app data from file: %s', str(fname))
            self._load_app_data(fname)
            logger.info('Load complete.')
        except Exception as exc:
            self.log_error(logger, exc)


def display_ui(dev_mode=False):
    app_data = {AppDataKeys.DEV_MODE: dev_mode}
    main_dashboard = MainDashboard(app_data)
    main_dashboard.display()
    if dev_mode:
        # Return the app_data for inspection
        return app_data


def get_assets_path() -> PurePath:
    """Return the path to the assets directory"""
    return Path(__file__).parent / 'assets'


def _get_logo_widget():
    """Function to create the CLEASE logo and return it in an image widget"""
    logo_path = get_assets_path() / 'clease_logo.png'
    with logo_path.open('rb') as file:
        logo = file.read()
    return widgets.Image(
        value=logo,
        format='png',
    )
