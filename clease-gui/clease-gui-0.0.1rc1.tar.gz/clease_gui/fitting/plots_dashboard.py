"""This dashboard is for the plots"""
import logging
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
import ipywidgets as widgets

import clease.plot_post_process
from clease_gui import register_logger, BaseDashboard, update_statusbar
import clease_gui as gui

__all__ = ['FitPlotDashboard']

logger = logging.getLogger(__name__)
register_logger(logger)


class FitPlotDashboard(BaseDashboard):
    def initialize(self):

        tabs = []
        titles = []

        plt.ioff()

        def add_tab(output, title):
            tabs.append(output)
            titles.append(title)
            with output:
                clear_output()

        self.fit_out = widgets.Output()
        add_tab(self.fit_out, 'Fit')

        self.residual_out = widgets.Output()
        add_tab(self.residual_out, 'Residuals')

        self.eci_out = widgets.Output()
        add_tab(self.eci_out, 'ECI')

        self.cv_out = widgets.Output()
        add_tab(self.cv_out, 'CV')

        self.convex_hull_out = widgets.Output()
        add_tab(self.convex_hull_out, 'Convex Hull')

        self.plot_btn = widgets.Button(description='Update Plots',
                                       button_style='primary')

        self.plot_btn.on_click(self._on_make_plot_click)

        self.tabs = widgets.Tab(children=tabs)
        for ii, title in enumerate(titles):
            self.tabs.set_title(ii, title)

        # Keep track of open figures, so we can close them again
        # if we overwrite them.
        self._figures = {}

    def display(self):
        display(self.plot_btn, self.tabs)

    @property
    def evaluator(self):
        try:
            return self.app_data[self.KEYS.EVALUATE]
        except KeyError:
            raise KeyError('No fit has been performed yet.')

    def _close_figure(self, name: str) -> None:
        """Close a figure object with a certain name
        if it exists"""
        if name in self._figures:
            logger.debug('Closing figure: %s', name)
            fig = self._figures[name]
            plt.close(fig=fig)
            # We no longer need to store this
            self._figures.pop(name)

    def _register_figure(self, name: str, fig) -> None:
        """Register a figure object with a name.
        Will close the old figure if it exists"""
        self._close_figure(name)
        self._figures[name] = fig

    def _make_convex_hull(self):
        evaluator = self.evaluator

        fig = clease.plot_post_process.plot_convex_hull(evaluator)

        with self.convex_hull_out:
            clear_output(wait=True)
            display(fig)
        self._register_figure('convex_hull', fig)

    def _make_residual_plot(self):
        evaluator = self.evaluator
        fig = clease.plot_post_process.plot_fit_residual(evaluator)
        btn = self._make_save_figure_button(fig, 'fit_residual.png')

        with self.residual_out:
            clear_output(wait=True)
            display(fig, btn)
        self._register_figure('residual', fig)

    def _make_cv_plot(self):
        evaluate = self.evaluator
        try:
            fig = clease.plot_post_process.plot_cv(evaluate)
            btn = self._make_save_figure_button(fig, 'fit_cv.png')
        except ValueError:
            # No CV scores
            fig = None
            btn = None

        with self.cv_out:
            clear_output(wait=True)
            if fig is not None:
                display(fig, btn)
                self._register_figure('cv_score', fig)
            else:
                print('No CV values, requires alpha optimization')

    def _make_fit_plot(self):
        evaluate = self.evaluator
        fig = clease.plot_post_process.plot_fit(evaluate)
        btn = self._make_save_figure_button(fig, 'fit_plot.png')

        with self.fit_out:
            clear_output(wait=True)
            display(fig, btn)
        self._register_figure('fit_plot', fig)

    def _make_eci_plot(self):
        evaluate = self.evaluator
        fig = clease.plot_post_process.plot_eci(evaluate)
        btn = self._make_save_figure_button(fig, 'fit_eci.png')

        with self.eci_out:
            clear_output(wait=True)
            display(fig, btn)
        self._register_figure('eci_plot', fig)

    def _make_save_figure_button(self, fig, filename):
        button = widgets.Button(description='Save Figure')

        def _on_click(b):
            cwd = self.app_data[self.KEYS.CWD]
            pa = cwd / filename
            fig.savefig(filename, dpi=400)
            logger.info('Saved figure to file: %s', str(pa))

        button.on_click(_on_click)
        return button

    @update_statusbar
    @gui.utils.disable_cls_widget('plot_btn')
    def _on_make_plot_click(self, b):
        try:
            self._make_fit_plot()
            self._make_residual_plot()
            self._make_eci_plot()
            self._make_cv_plot()
            self._make_convex_hull()
        except Exception as exc:
            logger.error(exc)

    @property
    def fit_results(self):
        return self.app_data.get('fit_results', None)
