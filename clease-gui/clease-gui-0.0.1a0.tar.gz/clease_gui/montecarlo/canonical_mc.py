import logging
import uuid
import threading
from IPython.display import display, clear_output
import ipywidgets as widgets
import numpy as np
import clease
from clease.montecarlo import constraints
import clease_gui as gui

__all__ = ['CanonicalMC']

logger = logging.getLogger(__name__)
gui.register_logger(logger)

# Register the clease MC logger specifically.
# Allows to follow the internal messages from the MC object.
# clease_mc_logger = logging.getLogger('clease.montecarlo.montecarlo')
# gui.register_logger(clease_mc_logger)


class CanonicalMC(gui.BaseDashboard):
    def __init__(self, *args, **kwargs):
        self._mc = None  # MC process
        super().__init__(*args, **kwargs)

    def initialize(self):
        # Temperature widgets

        self.temperature_mode_widget = widgets.Dropdown(
            description='MC mode:',
            options=[('Fixed Temperature', 'temp_fixed'),
                     ('Simulated annealing (linear spacing)',
                      'temp_range_linspace'),
                     ('Simulated annealing (logarithmic spacing)',
                      'temp_range_logspace')],
            value='temp_range_logspace',
            **self.DEFAULT_STYLE_KWARGS,
        )

        temp_range_linear = make_spacing_boxes(
            style_kwargs=self.DEFAULT_STYLE_KWARGS, )

        temp_range_log = make_spacing_boxes(
            style_kwargs=self.DEFAULT_STYLE_KWARGS, )

        self.temp_widgets = {
            'temp_fixed':
            widgets.BoundedFloatText(
                value=300,
                min=0,
                max=9999999,
                description='Temperature:',
                **self.DEFAULT_STYLE_KWARGS,
            ),
            'temp_range_linspace':
            temp_range_linear,
            'temp_range_logspace':
            temp_range_log,
        }
        self.temp_mode_output = widgets.Output()
        self._update_temp_mode()

        def _on_temp_mode_change(change):
            """Update the steps_output display whenever we change the dropdown"""
            if gui.utils.is_value_change(change):
                self._update_temp_mode()

        self.temperature_mode_widget.observe(_on_temp_mode_change)

        # MC logging frequency
        self.update_freq_widget = widgets.BoundedIntText(
            value=30,
            min=1,
            max=9999999,
            description='Update freq. (sec):',
            **self.DEFAULT_STYLE_KWARGS,
        )

        self.update_freq_help_msg = widgets.Label(
            value='Frequency of the logging from the MC run (in seconds).')

        self.step_mode_help = widgets.Label(
            '1 sweep runs equals <number of atoms in supercell> steps.')

        # Number of steps

        self.step_widgets = {}
        sweeps_widget = widgets.BoundedIntText(
            description='Number of sweeps:',
            value=1,
            min=1,
            max=99999999,
            **self.DEFAULT_STYLE_KWARGS,
        )
        self.step_widgets['sweeps'] = sweeps_widget

        steps_widget = widgets.BoundedIntText(
            description='Number of steps:',
            value=100,
            min=1,
            max=999999999999999,
            **self.DEFAULT_STYLE_KWARGS,
        )
        self.step_widgets['steps'] = steps_widget

        self.steps_output = widgets.Output()
        # Dropdown for selecting the step mode
        self.step_mode_widget = widgets.Dropdown(
            options=[
                ('Sweeps', 'sweeps'),
                ('Steps', 'steps'),
            ],
            description='Step mode:',
            value='sweeps',
            **self.DEFAULT_STYLE_KWARGS,
        )
        self._update_step_mode_output()  # update the steps_output

        def _on_step_mode_change(change):
            """Update the steps_output display whenever we change the dropdown"""
            if gui.utils.is_value_change(change):
                self._update_step_mode_output()

        self.step_mode_widget.observe(_on_step_mode_change)

        self.run_mc_button = widgets.Button(description='Run MC',
                                            button_style='primary')
        self.run_mc_button.on_click(self._on_run_mc_click)

        self.update_atoms_after_run_widget = widgets.Checkbox(
            description='Update supercell after MC run?', value=True)

        self.clear_mc_app_data_button = widgets.Button(
            description='Clear MC data')
        self.clear_mc_app_data_button.on_click(self._on_clear_mc_data)

        # Button for stopping the MC process
        self.stop_mc_button = widgets.Button(description='Abort MC',
                                             button_style='warning')
        self.stop_mc_button.on_click(self._on_stop_mc_click)

        self.mc_progress = widgets.IntProgress()
        self.mc_progress_label = widgets.Label()

        self.constrain_sublattices_wdgt = widgets.Checkbox(
            value=True,
            description='Constrain swaps by sublattice?',
            **self.DEFAULT_STYLE_KWARGS)

    def attach_constraints(
            self, mc: clease.montecarlo.Montecarlo,
            settings: clease.settings.ClusterExpansionSettings) -> None:
        if self.constrain_sublattices_wdgt.value:
            atoms = mc.atoms
            cnst = constraints.ConstrainSwapByBasis(atoms,
                                                    settings.index_by_basis)
            mc.generator.add_constraint(cnst)

    @property
    def update_after_run(self) -> bool:
        """Do we update the supercell in app_data after
        a completed MC run?"""
        return self.update_atoms_after_run_widget.value

    def display(self):
        frq_box = widgets.HBox(children=[
            self.update_freq_widget,
            self.update_freq_help_msg,
        ])
        step_mode_box = widgets.HBox(children=[
            self.step_mode_widget,
            self.step_mode_help,
        ])

        # place update atoms checkbox next to run MC button
        run_mc_box = widgets.HBox(
            children=[
                self.run_mc_button,
                self.stop_mc_button,
                self.update_atoms_after_run_widget,
            ],
            layout=dict(justify_content='space-between'),
        )

        display(step_mode_box, self.steps_output)
        display(self.temperature_mode_widget, self.temp_mode_output)
        display(frq_box, self.constrain_sublattices_wdgt)
        display(self.clear_mc_app_data_button)

        display(run_mc_box)
        mc_progress_box = widgets.HBox(children=[
            self.mc_progress,
            self.mc_progress_label,
        ])
        display(mc_progress_box)

    @property
    def active_temp_mode(self):
        return self.temperature_mode_widget.value

    @property
    def active_temp_mode_widget(self):
        return self.temp_widgets[self.active_temp_mode]

    def _update_temp_mode(self):
        with self.temp_mode_output:
            clear_output(wait=True)
            display(self.active_temp_mode_widget)

    def get_temp(self):
        mode = self.active_temp_mode
        widget = self.active_temp_mode_widget
        if mode == 'temp_fixed':
            value = widget.value
            return np.array([value])
        elif mode == 'temp_range_linspace':
            t_max = widget.children[0].value
            t_min = widget.children[1].value
            t_steps = widget.children[2].value
            return np.linspace(t_max, t_min, t_steps)
        elif mode == 'temp_range_logspace':
            t_max = widget.children[0].value
            t_min = widget.children[1].value
            t_steps = widget.children[2].value
            # Logspace is in base 10 by default
            return np.logspace(np.log10(t_max), np.log10(t_min), t_steps)
        raise ValueError(f'Unknown mode: {mode}')

    def _get_key(self, key):
        try:
            return self.app_data[key]
        except KeyError:
            raise KeyError(
                f'No key named {key} in app data. Must be loaded/created first.'
            )

    @property
    def active_step_mode(self):
        return self.step_mode_widget.value

    @property
    def active_step_mode_widget(self):
        mode = self.active_step_mode
        return self.step_widgets[mode]

    def _update_step_mode_output(self):
        with self.steps_output:
            clear_output(wait=True)
            display(self.active_step_mode_widget)

    def get_number_of_steps(self):
        mode = self.active_step_mode
        value = self.active_step_mode_widget.value
        if mode == 'sweeps':
            return value * len(self.atoms)
        assert mode == 'steps'
        return value

    @property
    def atoms(self):
        return self._get_key(self.KEYS.SUPERCELL)

    @property
    def eci(self):
        return self._get_key(self.KEYS.ECI)

    @property
    def settings(self):
        return self._get_key(self.KEYS.SETTINGS)

    @property
    def update_freq(self):
        return self.update_freq_widget.value

    def set_supercell(self, supercell):
        self.app_data[self.KEYS.SUPERCELL] = supercell

    def _make_mc_object(self, atoms, temp=200):
        eci = self.eci
        settings = self.settings

        # attach a CLEASE calculator
        atoms = clease.calculator.attach_calculator(settings, atoms, eci=eci)

        mc = clease.montecarlo.Montecarlo(atoms, temp)
        mc.status_every_sec = self.update_freq

        self.attach_constraints(mc, settings)

        return mc

    def _on_clear_mc_data(self, b):
        """Remove all data from previous MC runs"""
        try:
            del self.app_data[self.KEYS.CANONICAL_MC_DATA]
            logger.info('MC data has been cleared')
        except KeyError:
            logger.info('No MC data to clear.')
            # There was no data
            pass

    def set_mc_data(self, data):
        self.app_data[self.KEYS.CANONICAL_MC_DATA] = data

    @property
    def mc_data(self) -> list:
        return self._get_key(self.KEYS.CANONICAL_MC_DATA)

    def get_mc_data(self) -> list:
        """Return existing app data if it exists, otherwise return a new
        MC data list."""
        try:
            return self.mc_data
        except KeyError:
            # No data exists, create a new data dictionary
            # and insert it
            data = []
            self.set_mc_data(data)
            return self.mc_data

    def _on_stop_mc_click(self, b):
        """Set a termination flag in the currently active MC object,
        if there is one"""
        if self._mc is None:
            return
        self._mc.quit = True

    def _check_required_keys(self) -> None:
        """Check that relevant keys  for a MC run is present.
        Raises an error if that's not the case.
        """
        missing_keys = []
        for key in (self.KEYS.SUPERCELL, self.KEYS.SETTINGS, self.KEYS.ECI):
            if key not in self.app_data:
                missing_keys.append(key)
        if len(missing_keys) > 0:
            missing_keys = ', '.join(missing_keys)
            raise KeyError(
                f'Missing the following in app data: "{missing_keys}".')

    def _run_mc_in_thread(self) -> None:
        """Start the `_run_mc` method in a separate thread,
        while also disabling the run mc button for the duration
        of the run
        """
        @gui.update_statusbar
        def runner(self):
            """Helper function to be executed by the thread"""
            # Disable the run MC button while an MC thread is running
            try:
                with gui.utils.disable_widget_context(self.run_mc_button):
                    self._run_mc()
            except Exception as exc:
                self.log_error(logger, exc)

        # First we check if we have all necessary quantities, before
        # launching the thread
        self._check_required_keys()

        # The update_statusbar decorator assumes "self" is the first argument
        threading.Thread(target=runner, args=(self, ), daemon=True).start()

    def _run_mc(self):
        """Execute the MC run at the currnet settings."""
        # Some initialization
        temperatures = self.get_temp()
        n_temp = len(temperatures)

        mc_app_data = self.get_mc_data()
        data = {}
        mc_app_data.append(data)

        # Initial atoms object, current working atoms
        atoms = self.atoms

        def check_abort(mc):
            """Helper function to raise if we abort the MC.
            Raises an error, to break the thread which is running
            it"""
            if mc.quit:
                val = self.mc_progress_label.value
                self.mc_progress_label.value = val + '. MC aborted!'
                raise RuntimeError('MC was aborted.')

        mc = self._make_mc_object(atoms)
        # Add emin observer
        emin_obs = clease.montecarlo.observers.LowestEnergyStructure(mc.atoms)
        mc.attach(emin_obs)
        self._mc = mc
        # Initialize the progress bar
        self.mc_progress.value = 0
        self.mc_progress.max = n_temp

        try:
            for ii, temp in enumerate(temperatures):
                # Update progress bar
                self.mc_progress.value += 1
                prog = (ii + 1) / n_temp * 100  # Progress in percentage
                self.mc_progress_label.value = (
                    f'{prog:.1f}%, {ii+1}/{n_temp}. '
                    f'Current temp: {temp:.1f} K')

                # Initialize MC things
                check_abort(mc)
                mc.T = temp
                steps = self.get_number_of_steps()
                initial_energy = mc.atoms.get_potential_energy()

                # some debugging logging
                logger.debug(
                    'Starting MC run at T = %.3f K. Running a total of %d MC steps.',
                    temp, steps)
                # Simmulated annealing
                logger.debug(
                    'Annealing: Temperature step %d of %d. Current temperature: %.3f K.',
                    ii + 1,
                    n_temp,
                    temp,
                )

                mc.run(steps)  # Execute the MC
                check_abort(mc)  # Check if we exited because of an abort
                logger.debug('MC done after %d MC steps.', steps)
                logger.debug('Energy before MC: %.3f eV.', initial_energy)
                logger.debug('Lowest energy achieved during run: %.3f eV.',
                             emin_obs.lowest_energy)
                self._update_mc_data(mc, emin_obs, data)
                # Update the atoms object to the current emin, and continue from that
                atoms = emin_obs.emin_atoms

            if self.update_after_run:
                # "atoms" is now the emin atoms
                self.set_supercell(atoms)
                logger.info(
                    'Updated supercell to minimum energy configuration')

            logger.info('MC run complete.')
        finally:
            self._mc = None

    @gui.update_statusbar
    def _on_run_mc_click(self, b):
        try:
            self._run_mc_in_thread()
        except Exception as exc:
            logger.error(exc)

    def _make_mc_data(self, mc: clease.montecarlo.Montecarlo,
                      emin_obs) -> dict:
        """Create a dictionary with the relevant data from the MC run.
        We pass in the relevant emin observer as well, because we always want this data."""
        lowest_energy = emin_obs.lowest_energy
        temp = mc.T
        accept_rate = mc.num_accepted / mc.current_step
        mean_energy = mc.mean_energy.mean

        data = dict(
            emin=lowest_energy,
            mean_energy=mean_energy,
            temperature=temp,
            accept_rate=accept_rate,
        )
        return data

    def _update_mc_meta(self, mc, current_data):
        """Add metadata to the current data results"""
        atoms = mc.atoms
        current_meta = current_data.get('meta', {})
        meta = dict(
            natoms=len(atoms),
            formula=atoms.get_chemical_formula(),
            temp_mode=self.active_temp_mode,
        )
        current_meta.update(meta)
        if 'run_id' not in current_meta:
            current_meta['run_id'] = str(uuid.uuid4())
        current_data['meta'] = current_meta

    def _update_mc_data(self, mc: clease.montecarlo.Montecarlo, emin_obs,
                        current_data) -> None:
        """Update the current data with the new data"""
        new_data = self._make_mc_data(mc, emin_obs)
        self._update_mc_meta(mc, current_data)

        for key, value in new_data.items():
            if key not in current_data:
                # Add an empty list if this key has not been added yet
                # (emulating a defaultdict)
                current_data[key] = []
            current_data[key].append(value)


def make_spacing_boxes(min=300, max=30000, steps=25, style_kwargs=None):
    style_kwargs = style_kwargs or {}
    temp_range_min = widgets.BoundedFloatText(
        description='Temp (min):',
        min=1,
        max=99999999,
        value=min,
        **style_kwargs,
    )
    temp_range_max = widgets.BoundedFloatText(
        description='Temp. (max):',
        min=1,
        max=99999999,
        value=max,
        **style_kwargs,
    )
    temp_range_steps = widgets.BoundedIntText(
        description='Number of temp. steps:',
        min=1,
        max=99999999,
        value=steps,
        **style_kwargs,
    )

    temp_range_box = widgets.VBox(
        children=[temp_range_max, temp_range_min, temp_range_steps],
        layout=dict(justify_content='space-between'),
    )
    return temp_range_box
