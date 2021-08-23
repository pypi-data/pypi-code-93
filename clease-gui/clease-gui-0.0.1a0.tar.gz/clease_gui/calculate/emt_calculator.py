import logging
from IPython.display import display
import ipywidgets as widgets

import ase
from ase.optimize import BFGS
from ase.constraints import UnitCellFilter
from ase.calculators.emt import EMT
import clease

from clease_gui import register_logger, update_statusbar, BaseDashboard
import clease_gui as gui

logger = logging.getLogger(__name__)
register_logger(logger)


class EMTDashboard(BaseDashboard):
    def initialize(self):

        self.calc_button = widgets.Button(description='Calculate with EMT',
                                          button_style='primary')
        self.calc_button.on_click(self._on_calc_click)

        self.optimize_cell_widget = widgets.Checkbox(
            description='Optimize cell?',
            value=True,
            **self.DEFAULT_STYLE_KWARGS,
        )

        self.fmax_widget = widgets.BoundedFloatText(
            value=.02,
            min=1e-4,
            max=999,
            description='Max Force:',
            **self.DEFAULT_STYLE_KWARGS)

        def _on_update_optimize(change):
            if gui.utils.is_value_change(change):
                self._update_widgets()

        self.optimize_cell_widget.observe(_on_update_optimize)
        self._update_widgets()

    def _update_widgets(self):
        # disable fmax if we don't optimize
        fmax_disabled = not self.do_optimize
        self.fmax_widget.disabled = fmax_disabled

    @property
    def fmax(self):
        return self.fmax_widget.value

    @property
    def do_optimize(self):
        return self.optimize_cell_widget.value

    @update_statusbar
    @gui.utils.disable_cls_widget('calc_button')
    def _on_calc_click(self, b):
        try:
            self.calculate()
        except Exception as exc:
            self.log_error(logger, 'Failed to calculate: %s', exc)

    @property
    def mode(self):
        if self.do_optimize:
            return 'Optimization'
        return 'Static'

    def calculate(self):
        settings = self.app_data[self.KEYS.SETTINGS]
        if settings is None:
            raise RuntimeError('Need to know the settings to calculate')
        db_name = str(self.get_db_name())
        con = ase.db.connect(settings.db_name)
        num_calculated = 0

        mode = self.mode
        for row in con.select(converged=False):
            logger.info('Calculating row id: %d. Mode: %s', row.id, mode)
            atoms = row.toatoms()
            self._calculate_atoms(atoms)
            custom_kvp = row.key_value_pairs.copy()
            for key in ('struct_type', 'name', 'converged', 'started',
                        'queued'):
                # These keys are set in CLEASE, pop them out
                # pop converged just because we leave that as an "initial" attribute
                custom_kvp.pop(key, None)

            clease.tools.update_db(uid_initial=row.id,
                                   final_struct=atoms,
                                   db_name=db_name,
                                   custom_kvp_final=custom_kvp)
            num_calculated += 1
        if num_calculated == 0:
            logger.info('No calculations were performed.')
        else:
            logger.info(f'Complated {num_calculated} calculations.')

    def _calculate_atoms(self, atoms):
        calc = EMT()
        atoms.calc = calc
        if self.do_optimize:
            ucf = UnitCellFilter(atoms)
            opt = BFGS(ucf, logfile=None)
            fmax = self.fmax
            opt.run(fmax=fmax)
        else:
            atoms.get_potential_energy()

    def display(self):
        box = widgets.HBox(
            children=[self.optimize_cell_widget, self.fmax_widget])
        display(box, self.calc_button)
