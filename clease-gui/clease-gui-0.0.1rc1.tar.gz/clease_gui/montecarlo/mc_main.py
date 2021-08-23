from IPython.display import display
import ipywidgets as widgets
from clease_gui import BaseDashboard
from . import CanonicalMC, PlotMCDashboard, MCRunDashboard

__all__ = ['MainMCDashboard']


class MainMCDashboard(BaseDashboard):
    def initialize(self):
        self.canonical_mc_out = widgets.Output()
        self.canonical_mc_dashboard = CanonicalMC(self.app_data)
        with self.canonical_mc_out:
            self.canonical_mc_dashboard.display()

        self.plot_out = widgets.Output(layout={'height': '100%'})
        self.plot_dashboard = PlotMCDashboard(self.app_data)
        with self.plot_out:
            self.plot_dashboard.display()

        self.store_mc_run_out = widgets.Output()
        self.store_mc_dashboard = MCRunDashboard(self.app_data)
        with self.store_mc_run_out:
            self.store_mc_dashboard.display()

        self.tab = widgets.Tab(children=[
            self.canonical_mc_out,
            self.plot_out,
            self.store_mc_run_out,
        ])

        self.tab.set_title(0, 'Canonical MC')
        self.tab.set_title(1, 'Plotting')
        self.tab.set_title(2, 'MC Runs')

    def display(self):
        display(self.tab)
