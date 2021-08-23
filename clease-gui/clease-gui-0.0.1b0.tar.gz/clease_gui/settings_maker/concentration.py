import logging
from IPython.display import display, clear_output
import ipywidgets as widgets
from ase.data import atomic_numbers
from clease.settings import Concentration

from clease_gui import BaseDashboard, update_statusbar
import clease_gui as gui

__all__ = ['ConcentrationDashboard']

logger = logging.getLogger(__name__)
gui.register_logger(logger)


class ConcentrationDashboard(BaseDashboard):
    def initialize(self):
        self.basis_elements = []
        self.basis_text_box = widgets.Text(description='Basis:')
        self.out_basis = widgets.Output(layout=widgets.Layout(
            border='solid 1px'))

        self.add_basis_b = widgets.Button(description='Add basis')
        self.remove_basis_b = widgets.Button(description='Remove last basis')
        self.clear_basis_b = widgets.Button(description='Clear basis')

        self.add_basis_b.on_click(self._on_add_basis)
        self.remove_basis_b.on_click(self._on_remove_last_basis)
        self.clear_basis_b.on_click(self._on_clear_basis)

    def display(self):
        print('Add or remove basis elements to the concentration')
        self.update_basis_out()

        display(
            self.basis_text_box,
            self.add_basis_b,
            self.remove_basis_b,
            self.clear_basis_b,
            self.out_basis,
        )

    def update_basis_out(self):
        with self.out_basis:
            clear_output()
            print('Current basis:', self.basis_elements)

    def add_basis(self, basis):
        for element in basis:
            if element not in atomic_numbers:
                self.bad_basis_element(element)
                return
        self.basis_elements.append(basis)
        self.update_basis_out()

    def bad_basis_element(self, element):
        self.update_basis_out()
        with self.out_basis:
            print('Bad element found:', element)

    @update_statusbar
    def _on_add_basis(self, b):
        value = self.basis_text_box.value

        # Replace newlines with , for string manupulation
        DELIM = ' '
        value = value.replace('\n', DELIM)
        value = value.replace(',', DELIM)
        value = value.replace(';', DELIM)

        if not value:
            # Button was clicked without adding any elements
            return

        new_basis = [
            val.strip() for val in value.strip().split(DELIM) if val.strip()
        ]
        self.add_basis(new_basis)

    def remove_last_basis(self, update=True):
        try:
            self.basis_elements.pop()
        except IndexError:
            # Empty
            pass
        if update:
            self.update_basis_out()

    @update_statusbar
    def _on_remove_last_basis(self, b):
        self.remove_last_basis()

    @update_statusbar
    def _on_clear_basis(self, b):
        tot = len(self.basis_elements)
        for _ in range(tot):
            self.remove_last_basis(update=False)
        self.update_basis_out()

    def get_concentration(self):
        return Concentration(basis_elements=self.basis_elements)

    def set_widgets_from_load(self, conc: Concentration) -> None:
        logger.debug('Updating conc widgets')
        self.basis_elements = conc.basis_elements
        self.update_basis_out()
