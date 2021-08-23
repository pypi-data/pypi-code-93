import logging
from IPython.display import display, clear_output
import ipywidgets as widgets
import numpy as np
from clease.settings import ClusterExpansionSettings
from clease_gui import utils, BaseDashboard
import clease_gui as gui
from . import settings_buttons as swidgets

__all__ = ['SettingsDashboard']

logger = logging.getLogger(__name__)
gui.register_logger(logger)

DESC_WIDTH = '150px'
STYLE = {'description_width': DESC_WIDTH}


class SettingsDashboard(BaseDashboard):
    def initialize(self):
        self.cell_size = (3, 3, 3)
        self.out_size = widgets.Output()

        # Buttons related to the settings type,
        # CEBulk, CECrystal and CESlab

        # Output object for type buttons
        self.out_type = widgets.Output()
        self.out_help = widgets.Output()

        self.type_buttons_dct = {
            'CEBulk':
            swidgets.CEBulkButtons(self.app_data, output=self.out_type),
            'CECrystal':
            swidgets.CECrystalButtons(self.app_data, output=self.out_type),
            'CESlab':
            swidgets.CESlabButtons(self.app_data, output=self.out_type),
        }
        self.type_mode_b = widgets.Dropdown(
            options=[
                ('Bulk', 'CEBulk'),
                # Not yet supported
                # ('Crystal', 'CECrystal'),
                # ('Slab', 'CESlab'),
            ],
            description='Type:',
            layout={'width': 'max-content'},
            style=STYLE,
        )

        # Add observer to the type, so we know if we need to update the button collection
        def on_type_mode_change(change):
            if utils.is_value_change(change):
                self.update_type_mode()

        self.type_mode_b.observe(on_type_mode_change)

        self.size_mode_out = widgets.Output()
        self.size_mode_widgets = {
            'fixed':
            swidgets.FixedSizeMode(output=self.size_mode_out),
            'supercell_factor':
            swidgets.SupercellFactorSizeMode(output=self.size_mode_out),
        }
        self.size_mode_b = widgets.Dropdown(options=[('Fixed', 'fixed'),
                                                     ('Supercell Factor',
                                                      'supercell_factor')],
                                            value='supercell_factor',
                                            description='Size mode:',
                                            **self.DEFAULT_STYLE_KWARGS)
        self.size_mode_b.observe(self._on_size_mode_change)

    def update_type_mode(self):
        self.type_buttons.display_widgets()

    @property
    def type_buttons(self):
        mode = self.type_mode_b.value
        return self.type_buttons_dct[mode]

    def display(self):

        display(self.type_mode_b)
        display(self.out_type)
        self.update_type_mode()

        # Buttons for size mode
        with self.size_mode_out:
            self.active_size_mode_widget.display_widgets()
        display(self.size_mode_b, self.size_mode_out)

    @property
    def type_mode(self):
        return self.type_mode_b.value

    def get_type_kwargs(self):
        return self.type_buttons.value

    @property
    def active_size_mode(self):
        return self.size_mode_b.value

    @property
    def active_size_mode_widget(self):
        return self.size_mode_widgets[self.active_size_mode]

    def _on_size_mode_change(self, change):
        if utils.is_value_change(change):
            self._update_size_mode_widget()

    def _update_size_mode_widget(self):
        logger.debug('Updating active size mode widget')
        with self.size_mode_out:
            clear_output(wait=True)
            self.active_size_mode_widget.display_widgets()

    def get_settings_kwargs(self):
        size_kwargs = self.active_size_mode_widget.value
        kwargs = dict(
            type=self.type_mode,
            **size_kwargs,
            **self.get_type_kwargs(),
        )
        return kwargs

    def set_widgets_from_load(self,
                              settings: ClusterExpansionSettings) -> None:
        # Figure out what the builder was
        kwargs = settings.kwargs
        factory = kwargs.get('factory', None)
        if factory != 'CEBulk':
            logger.debug('Cannot load settings of factory type: %s', factory)
            return

        # Let's try and load things
        self._load_cebulk_settings(settings)

    def _load_cebulk_settings(self,
                              settings: ClusterExpansionSettings) -> None:
        mode = 'CEBulk'
        self.type_mode_b.value = mode
        self.update_type_mode()

        # Get some factory keys
        for key in ('crystalstructure', 'a', 'c', 'c_over_a'):
            value = settings.kwargs.get(key, None)
            if value is not None:
                self.type_buttons.set_widget_value(key, value)

        # Guess the size mode
        if settings.size is None:
            logger.debug('Detected supercell factor mode')
            # use supercell factor
            self.size_mode_b.value = 'supercell_factor'
            self._update_size_mode_widget()
            scf = settings.supercell_factor
            skew = settings.skew_threshold
            self.active_size_mode_widget.set_widget_value(
                'supercell_factor', scf)
            self.active_size_mode_widget.set_widget_value(
                'skew_threshold', skew)
        else:
            logger.debug('Detected fixed size mode')
            self.size_mode_b.value = 'fixed'
            # self._update_size_mode_widget()
            logger.debug('Getting size value')
            value = settings.size  # in 3x3 matrix
            # Use diagonal
            value = np.diag(value)
            value = ', '.join(map(str, value))
            logger.debug('Setting widget %s to value %s', key, value)
            self.active_size_mode_widget.set_widget_value('size', value)

        # Settings stored directly in the settings object
        all_keys = ('basis_func_type', 'db_name', 'max_cluster_size',
                    'max_cluster_dia', 'include_background_atoms')
        for key in all_keys:
            value = get_value_for_widget(settings, key)
            logger.debug('Setting %s to %s', key, value)
            self.type_buttons.set_widget_value(key, value)


def get_value_for_widget(settings, key):
    """Get a value from the settings, and sanitize it for settings
    a widget state """
    if key == 'basis_func_type':
        return settings.basis_func_type.name
    if key == 'db_name':
        value = settings.db_name
        return value
    if key == 'max_cluster_size':
        return settings.max_cluster_size
    if key == 'max_cluster_dia':
        mcd = settings.max_cluster_dia
        mcd = mcd[2:]  # Skip first two, they're 0 and 1 body clusters
        return mcd
    if key == 'include_background_atoms':
        return settings.include_background_atoms

    raise ValueError(f'Cannot deal with key: {key}')
