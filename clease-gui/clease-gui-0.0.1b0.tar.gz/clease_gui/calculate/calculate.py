from IPython.display import display, clear_output
import ipywidgets as widgets
from clease_gui import BaseDashboard
from .emt_calculator import EMTDashboard

__all__ = ['CalculateDashboard']


class CalculateDashboard(BaseDashboard):
    def initialize(self):
        self.emt_out = widgets.Output()
        emt_dash = EMTDashboard(self.app_data)
        with self.emt_out:
            clear_output()
            emt_dash.display()

    def display(self):
        display(self.emt_out)
