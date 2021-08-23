import logging
import random
from collections import Counter
from typing import Tuple
from IPython.display import display, clear_output
import ipywidgets as widgets
import ase
import ase.visualize
import clease
from clease_gui import BaseDashboard, register_logger, update_statusbar, utils

__all__ = ['SupercellDashboard']

logger = logging.getLogger(__name__)
register_logger(logger)


class SupercellDashboard(BaseDashboard):
    def initialize(self):

        self.sc_widgets = []
        for coord in ('x', 'y', 'z'):
            wdgt = widgets.BoundedIntText(description=f'Repetition ({coord}):',
                                          value=5,
                                          min=1,
                                          max=999,
                                          **self.DEFAULT_STYLE_KWARGS)
            self.sc_widgets.append(wdgt)

        self.make_atoms_btn = widgets.Button(
            description='Make random supercell',
            layout=self.DEFAULT_BUTTON_LAYOUT)
        self.make_atoms_btn.on_click(self._on_make_supercell_click)

        self.desc_label = widgets.Label(value=self.make_desc_label())

        self.view_atoms_btn = widgets.Button(
            description='View Current Supercell',
            layout=self.DEFAULT_BUTTON_LAYOUT)
        self.view_atoms_btn.on_click(self._on_view_atoms_click)

        self.load_supercell_button = widgets.Button(
            description='Load Supercell')
        self.load_supercell_text = widgets.Text(description='Filename:',
                                                value='supercell.traj')
        self.load_supercell_button.on_click(self._on_load_supercell_click)

        self.save_supercell_button = widgets.Button(
            description='Save Supercell')
        self.save_supercell_text = widgets.Text(description='Filename:',
                                                value='supercell.traj')
        self.save_supercell_button.on_click(self._on_save_supercell_click)

        self.species_output = widgets.Output()
        self.species_output.clear_output()

    def display(self):
        display(self.desc_label)
        vbox_sc_widgets = widgets.VBox(children=self.sc_widgets)

        hbox_buttons = widgets.HBox(children=[
            self.make_atoms_btn,
            self.view_atoms_btn,
        ])

        load_hbox = widgets.HBox(
            children=[self.load_supercell_button, self.load_supercell_text])
        save_hbox = widgets.HBox(
            children=[self.save_supercell_button, self.save_supercell_text])
        display(save_hbox, load_hbox)
        display(hbox_buttons)
        display(vbox_sc_widgets)
        display(self.species_output)

    def sc_formula_unit(self):
        try:
            supercell = self.supercell
        except ValueError:
            return ''
        else:
            return supercell.get_chemical_formula()

    @update_statusbar
    @utils.disable_cls_widget('load_supercell_button')
    def _on_load_supercell_click(self, b):
        try:
            self.load_supercell()
        except Exception as exc:
            logger.error(exc)

    def load_supercell(self):
        fname = self.load_supercell_text.value
        if fname == '':
            raise ValueError('No filename supplied')
        cwd = self.app_data[self.KEYS.CWD]
        fname = cwd / fname
        self._load_supercell(fname)

    def _load_supercell(self, fname):
        logger.info('Loading supercell from file: %s', fname)
        atoms = ase.io.read(fname)
        self.set_supercell(atoms)
        logger.info('Load successful.')

    def make_random_supercell(self):
        atoms = self.settings.prim_cell.copy()
        atoms *= self.repetitions

        self.settings.set_active_template(atoms)
        nib = [len(x) for x in self.settings.index_by_basis]
        x = self.concentration.get_random_concentration(nib)
        supercell = self._make_atoms_at_conc(x)
        self.set_supercell(supercell)

    @update_statusbar
    @utils.disable_cls_widget('view_atoms_btn')
    def _on_view_atoms_click(self, b):
        try:
            self._visualize_supercell()
            self._update_desc_label()
        except Exception as exc:
            logger.error(exc)

    def _visualize_supercell(self):
        supercell = self.supercell
        if supercell is None:
            raise ValueError('No supercell has been made yet.')
        ase.visualize.view(supercell)

    def make_desc_label(self):
        text = 'Create a supercell.'
        try:
            sc = self.supercell
        except ValueError:
            # No supercell present, just return initial text part
            return text
        formula_unit = sc.get_chemical_formula()
        ntot = len(sc)

        text += f' Current formula unit: {formula_unit}.'
        text += f' Total number of atoms: {ntot}'

        return text

    def _update_desc_label(self):
        self.desc_label.value = self.make_desc_label()

    def set_supercell(self, atoms: ase.Atoms, draw_species_output=True):
        # XXX: Do we want to set the active template here?
        self.settings.set_active_template(atoms)
        self.app_data[self.KEYS.SUPERCELL] = atoms
        self._update_desc_label()
        if draw_species_output:
            self._make_species_output()

    @property
    def supercell(self):
        try:
            return self.app_data[self.KEYS.SUPERCELL]
        except KeyError:
            raise ValueError('No supercell available in app data.')

    @property
    def repetitions(self) -> Tuple[int]:
        return tuple(wdgt.value for wdgt in self.sc_widgets)

    @update_statusbar
    @utils.disable_cls_widget('make_atoms_btn')
    def _on_make_supercell_click(self, b):
        try:
            self.make_random_supercell()
            logger.info('Supercell created.')
        except Exception as exc:
            logger.error(exc)
            return

    def _get_new_struct_obj(self):
        """Helper function for creating a NewStructures object"""
        return clease.structgen.NewStructures(self.settings)

    @property
    def concentration(self):
        return self.settings.concentration

    def _make_atoms_at_conc(self, x):
        new_struct = self._get_new_struct_obj()
        num_atoms_in_basis = [
            len(indices) for indices in self.settings.index_by_basis
        ]
        num_to_insert = self.concentration.conc_in_int(num_atoms_in_basis, x)
        return new_struct._random_struct_at_conc(num_to_insert)

    def save_supercell(self):
        supercell = self.supercell
        fname = self.save_supercell_text.value
        if fname == '':
            raise ValueError('No filename supplied.')
        fname = self.app_data[self.KEYS.CWD] / fname
        logger.info('Saving supercell to file: %s', fname)
        ase.io.write(fname, supercell)
        logger.info('Save successful.')

    @update_statusbar
    @utils.disable_cls_widget('save_supercell_button')
    def _on_save_supercell_click(self, b):
        try:
            self.save_supercell()
        except Exception as exc:
            logger.error(exc)

    def get_species_per_basis(self):
        settings = self.settings
        supercell = self.supercell

        idx_by_basis = settings.index_by_basis

        species_per_basis = []
        for idx in idx_by_basis:
            atoms = supercell[idx]
            species = Counter(atoms.symbols)
            species_per_basis.append(species)
        return species_per_basis

    def set_supercell_species(self, species_per_basis):
        # Check that all species per basis add up to the correct number
        # by comparing to the current total
        basis_elements = self.settings.basis_elements
        index_by_basis = self.settings.index_by_basis
        for ii, new_basis in enumerate(species_per_basis):
            cur_count = len(index_by_basis[ii])
            new_count = sum(new_basis.values())
            if cur_count != new_count:
                sublatt = ii + 1
                raise ValueError(
                    ('Incorrect number of elements in sublattice {}.'
                     ' Expected {}, but got {}.').format(
                         sublatt, cur_count, new_count))
        # Do the update, now we confirmed the counts are OK!
        atoms = self.supercell.copy()
        for ii, indices in enumerate(index_by_basis):
            new_syms = []
            for elem in basis_elements[ii]:
                new_syms.append
                new_count = species_per_basis[ii].get(elem, 0)
                new_syms.extend([elem] * new_count)
            assert len(new_syms) == len(indices), (len(new_syms), len(indices))
            # Shuffle sublattice
            random.shuffle(new_syms)
            atoms.symbols[indices] = new_syms
        # We don't need to redraw the species output widgets again
        self.set_supercell(atoms, draw_species_output=False)
        logger.info('Supercell updated.')

    def _make_species_output(self):
        out = self.species_output

        basis_elements = self.settings.basis_elements
        species_per_basis = self.get_species_per_basis()
        num_basis = len(basis_elements)

        with out:
            clear_output()

            all_elem_boxes = []
            tot_specified_boxes = []

            def update_tot():
                for ii in range(num_basis):
                    elem_boxes = all_elem_boxes[ii]
                    tot = sum(wdgt.value for wdgt in elem_boxes)
                    logger.debug('Updating total to %d', tot)
                    tot_box = tot_specified_boxes[ii]
                    tot_box.value = tot

            def observe_change(change):
                if utils.is_value_change(change):
                    update_tot()

            for ii, elements in enumerate(basis_elements):
                sublattice_out = widgets.Output(
                    layout={'border': '1px solid lightgray'})
                s = f'Sublattice {ii+1}'
                html = f"<h1 style='font-size:17px'> {s} </h1>"
                label = widgets.HTML(value=html)
                elem_boxes = []
                all_elem_boxes.append(elem_boxes)
                tot_in_basis = sum(species_per_basis[ii].values())
                # Box with total number in the basis
                tot_box = widgets.IntText(
                    description='Total in basis:',
                    value=tot_in_basis,
                    disabled=True,
                    style={'description_width': 'initial'})
                # Box with the total specified number in that basis
                tot_specified = widgets.IntText(
                    description='Total specified:',
                    value=0,
                    disabled=True,
                    style={'description_width': 'initial'})
                tot_specified_boxes.append(tot_specified)

                for elem in elements:
                    count = species_per_basis[ii][elem]
                    wdgt = widgets.BoundedIntText(value=count,
                                                  min=0,
                                                  max=tot_in_basis,
                                                  description=f'{elem}:')
                    wdgt.observe(observe_change)
                    elem_boxes.append(wdgt)

                hbox = widgets.HBox(children=[tot_specified, tot_box])
                with sublattice_out:
                    clear_output()
                    display(label, *elem_boxes, hbox)

                display(sublattice_out)
            update_supercell_btn = widgets.Button(
                description='Update supercell')
            display(update_supercell_btn)
        update_tot()

        def make_species_per_basis():
            count = []
            for ii, basis in enumerate(basis_elements):
                c = {}
                elem_boxes = all_elem_boxes[ii]
                for ii, elem in enumerate(basis):
                    c[elem] = elem_boxes[ii].value
                count.append(c)
            return count

        def on_update_click(b):
            try:
                with utils.disable_widget_context(update_supercell_btn):
                    self.set_supercell_species(make_species_per_basis())
            except Exception as exc:
                self.log_error(logger, exc)

        update_supercell_btn.on_click(on_update_click)
