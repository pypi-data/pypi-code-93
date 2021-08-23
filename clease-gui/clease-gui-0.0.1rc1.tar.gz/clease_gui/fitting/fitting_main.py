import logging
from IPython.display import display, clear_output
import ipywidgets as widgets
import clease
from clease_gui import register_logger, BaseDashboard, update_statusbar, utils
from .eci_fit import ECIFitDashboard
from .plots_dashboard import FitPlotDashboard

__all__ = ['FittingDashboard']

logger = logging.getLogger(__name__)
register_logger(logger, level=logging.DEBUG)


class FittingDashboard(BaseDashboard):
    def initialize(self):
        # Load ECI functionality
        self.load_eci_button = widgets.Button(description='Load ECI')
        self.load_eci_text = widgets.Text(description='Filename:',
                                          value='eci.json')
        self.load_eci_button.on_click(self._on_load_eci_click)

        # Save ECIs
        self.save_eci_button = widgets.Button(description='Save ECI')
        self.save_eci_text = widgets.Text(description='Filename:',
                                          value='eci.json')
        self.save_eci_button.on_click(self._on_save_eci_click)

        self.plotting_out = widgets.Output()
        self.fitting_eci_out = widgets.Output()
        eci_fit_dashboard = ECIFitDashboard(self.app_data)
        fit_plot_dashboard = FitPlotDashboard(self.app_data)

        with self.fitting_eci_out:
            clear_output()
            eci_fit_dashboard.display()

        with self.plotting_out:
            clear_output()
            fit_plot_dashboard.display()

        self.tab = widgets.Tab(children=[
            self.fitting_eci_out,
            self.plotting_out,
        ])

        self.tab.set_title(0, 'Fit ECI\'s')
        self.tab.set_title(1, 'Fit Plots')

    def display(self):
        load_hbox = widgets.HBox(
            children=[self.load_eci_button, self.load_eci_text])
        save_hbox = widgets.HBox(
            children=[self.save_eci_button, self.save_eci_text])
        display(load_hbox, save_hbox)
        display(self.tab)

    @update_statusbar
    @utils.disable_cls_widget('load_eci_button')
    def _on_load_eci_click(self, b):
        try:
            self._load_eci()
        except Exception as exc:
            logger.error(exc)

    def _load_eci(self):
        fname = self.load_eci_text.value
        if fname == '':
            raise ValueError('No filename supplied')
        fname = self.app_data[self.KEYS.CWD] / fname
        logger.info('Loading ECI from file: %s', fname)
        with fname.open() as file:
            eci = clease.jsonio.read_json(file)
        self.set_eci(eci)
        logger.info('Load successful.')

    @property
    def eci(self):
        try:
            return self.app_data[self.KEYS.ECI]
        except KeyError:
            raise ValueError(
                'No ECI\'s present. Run fit first, or load ECI from file.')

    def set_eci(self, value):
        self.app_data[self.KEYS.ECI] = value

    @update_statusbar
    @utils.disable_cls_widget('save_eci_button')
    def _on_save_eci_click(self, b):
        try:
            self._save_eci()
        except Exception as exc:
            logger.error('Error during saving: %s', exc)

    def _save_eci(self):
        eci = self.eci
        fname = self.save_eci_text.value
        if fname == '':
            raise ValueError('No filename supplied.')
        fname = self.app_data[self.KEYS.CWD] / fname
        logger.info('Saving ECI to file: %s', fname)
        with fname.open('w') as file:
            # Use CLEASE jsonio module to encode the ECI dict
            # since it contains NumPy arrays.
            clease.jsonio.write_json(file, eci)
        logger.info('Save successful.')
