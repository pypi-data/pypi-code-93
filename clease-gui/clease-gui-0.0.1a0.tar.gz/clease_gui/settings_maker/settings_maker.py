import logging
from IPython.display import display, clear_output
import ipywidgets as widgets

import clease
from clease.settings import CEBulk, CECrystal
from clease.tools import reconfigure
from clease_gui import register_logger, BaseDashboard, update_statusbar, utils
from . import ConcentrationDashboard, SettingsDashboard

__all__ = ['SettingsMakerDashboard']

logger = logging.getLogger(__name__)
register_logger(logger)


class SettingsMakerDashboard(BaseDashboard):
    """Have the concentration and settings dashboard under 1 tab"""
    def initialize(self):
        self.tab = None

        # dashboard = self  # Alias
        self.out_conc = widgets.Output()  # Concentration dashboard
        self.out_settings = widgets.Output()  # Settings dashboard

        self.make_settings_btn = widgets.Button(description='Make settings')
        self.make_settings_btn.on_click(self._on_make_settings_click)

        self.delete_settings_btn = widgets.Button(
            description='Delete settings', button_style='danger')
        self.delete_settings_btn.on_click(self._on_delete_settings_click)

        self.save_settings_btn = widgets.Button(description='Save settings')
        self.save_settings_fname = widgets.Text(description='Filename:',
                                                value='settings.json')
        self.save_settings_btn.on_click(self._on_save_settings_click)

        self.save_settings_box = widgets.HBox(children=[
            self.save_settings_btn,
            self.save_settings_fname,
        ])

        self.load_settings_btn = widgets.Button(description='Load settings')
        self.load_settings_fname = widgets.Text(description='Filename:',
                                                value='settings.json')
        self.load_settings_btn.on_click(self._on_load_settings_click)

        self.load_settings_box = widgets.HBox(children=[
            self.load_settings_btn,
            self.load_settings_fname,
        ])

        self._conc_dashboard = ConcentrationDashboard(self.app_data)
        with self.out_conc:
            clear_output()
            self._conc_dashboard.display()

        self._settings_dashboard = SettingsDashboard(self.app_data)
        with self.out_settings:
            clear_output()
            self._settings_dashboard.display()

        self.tab = widgets.Tab(children=[self.out_conc, self.out_settings])

        self.tab.set_title(0, 'Concentration')
        self.tab.set_title(1, 'Settings')

        self.reconfig_db_button = widgets.Button(description='Reconfigure DB')
        self.reconfig_db_button.on_click(self._on_reconfig_click)

    @update_statusbar
    @utils.disable_cls_widget('reconfig_db_button')
    def _on_reconfig_click(self, b):
        try:
            self.reconfig_db()
        except Exception as exc:
            self.log_error(logger, exc)

    def reconfig_db(self):
        settings = self.settings
        if settings is None:
            raise ValueError(
                'Settings has not been created yet, cannot reconfigure')
        # TODO: Account for CWD
        logger.info('Reconfiguring database: %s', settings.db_name)
        reconfigure(settings)
        logger.info('Reconfiguration complete.')

    def display(self):
        hbox_btn = widgets.HBox(
            children=[self.make_settings_btn, self.delete_settings_btn])
        display(
            hbox_btn,
            self.save_settings_box,
            self.load_settings_box,
            self.reconfig_db_button,
            self.tab,
        )

    def get_concentration(self):
        return self._conc_dashboard.get_concentration()

    @update_statusbar
    @utils.disable_cls_widget('make_settings_btn')
    def _on_make_settings_click(self, b):
        if self.settings is not None:
            logger.error(
                'Cannot make settings, a settings object already exists.')
            return
        logger.info('Making settings...')
        try:
            self.make_settings()
        except Exception as e:
            self.log_error(logger, 'Error when making settings: %s', e)
        else:
            logger.info('Done!')

    @update_statusbar
    @utils.disable_cls_widget('delete_settings_btn')
    def _on_delete_settings_click(self, b):
        try:
            self.app_data.pop(self.KEYS.SETTINGS)
            logger.info('Removed settings from app data')
        except KeyError:
            logger.info('No settings in app data, cannot delete.')

    def make_settings(self) -> None:
        """Combine the settings in the relevant dashboards, and create the settings"""
        conc = self.get_concentration()
        kwargs = self._settings_dashboard.get_settings_kwargs()
        skew_threshold = kwargs.pop('skew_threshold', None)
        settings_type = kwargs.pop('type')

        if settings_type == 'CEBulk':
            settings = CEBulk(conc, **kwargs)
        elif settings_type == 'CECrystal':
            settings = CECrystal(conc, **kwargs)
        elif settings_type == 'CESlab':
            # miller = settings_type.pop('miller')
            raise NotImplementedError('Not yet implemneted, yo!')
        else:
            raise ValueError(
                f'Something is wrong. Got unknown settings_type {settings_type}'
            )
        self.set_settings(settings)
        if skew_threshold is not None:
            self.settings.skew_threshold = skew_threshold

    @property
    def settings(self):
        """Get the settings from the app data"""
        return self.app_data.get(self.KEYS.SETTINGS, None)

    def set_settings(self, settings):
        """Insert settings into the app data"""
        self.app_data[self.KEYS.SETTINGS] = settings

    @property
    def cwd(self):
        return self.app_data[self.KEYS.CWD]

    def get_save_settings_fname(self):
        return self.cwd / self.save_settings_fname.value

    @update_statusbar
    @utils.disable_cls_widget('save_settings_btn')
    def _on_save_settings_click(self, b):
        try:
            fname = self.get_save_settings_fname()
            logger.info('Saving settings in file: %s', str(fname))
            self.save_settings(fname)
            logger.info('Save successful.')
        except Exception as exc:
            logger.error('Error during saving: %s', exc)

    def save_settings(self, fname):
        settings = self.settings
        if settings is None:
            raise RuntimeError('Settings has not been created yet.')
        settings.save(fname)

    def load_settings(self, fname) -> None:
        settings = clease.settings.settings_from_json(fname)
        self.set_settings(settings)
        self.set_settings_widget_states(settings)

    def get_load_settings_fname(self):
        return self.app_data[self.KEYS.CWD] / self.load_settings_fname.value

    @update_statusbar
    @utils.disable_cls_widget('load_settings_btn')
    def _on_load_settings_click(self, b):
        try:
            fname = self.get_load_settings_fname()
            logger.info('Loading settings from file: %s', str(fname))
            self.load_settings(fname)
            logger.info('Load successful.')
        except Exception as exc:
            self.log_error(logger, 'Error during loading: %s', exc)

    def set_settings_widget_states(self, settings):
        """Set the widget states from a new settings object"""
        conc = settings.concentration
        self._conc_dashboard.set_widgets_from_load(conc)
        self._settings_dashboard.set_widgets_from_load(settings)
