import logging
from IPython.display import display, clear_output
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import clease_gui as gui

__all__ = ['PlotMCDashboard']

logger = logging.getLogger(__name__)
gui.register_logger(logger)


class PlotMCDashboard(gui.BaseDashboard):
    def initialize(self):
        plt.ioff()
        self.mode_widget = widgets.Dropdown(
            description='MC mode:',
            options=[
                ('Canonical', 'canonical'),
            ],
            **self.DEFAULT_STYLE_KWARGS,
        )
        self.plot_tabs = []
        self.plot_outputs = []
        self.figures = []
        self.axes = []
        for _ in range(3):
            tab = widgets.Output()
            out = widgets.Output()
            with out:
                clear_output()
                with plt.style.context('seaborn'):
                    fig, ax = plt.subplots()
            self.plot_outputs.append(out)
            self.plot_tabs.append(tab)
            self.figures.append(fig)
            self.axes.append(ax)

            # Create save fig button/text
            box = self._make_savefig_box(fig)
            with tab:
                clear_output()
                display(out, box)

        self.update_button = widgets.Button(description='Update')
        self.update_button.on_click(self._on_update_click)

        self.x_axis_style_widget = widgets.Dropdown(
            description='x axis scale:',
            options=[
                ('Linear', 'linear'),
                ('Logarithmic', 'log'),
            ])
        self.x_axis_style_widget.observe(self._on_x_axis_change)
        self.plots_tabs = widgets.Tab(children=self.plot_tabs)
        self.plots_tabs.set_title(0, 'Min. Energy')
        self.plots_tabs.set_title(1, 'Avg. Energy')
        self.plots_tabs.set_title(2, 'Accept Rate')
        self.invert_temp_axis = widgets.Checkbox(
            value=True,
            description='Reverse temperature axis?',
            **self.DEFAULT_STYLE_KWARGS)

    def display(self):
        top_widgets = widgets.HBox(children=[
            self.update_button,
            self.x_axis_style_widget,
        ])
        display(top_widgets)
        display(self.invert_temp_axis, self.mode_widget)

        display(self.plots_tabs)

    def get_key(self, key):
        """Helper function which raises a more useful error message"""
        try:
            return self.app_data[key]
        except KeyError:
            raise KeyError((f'No key {key} available in app data. '
                            'Did you forget to load/run simulation first?'))

    def get_data(self):
        mode = self.active_mc_mode
        if mode == 'canonical':
            return self.get_key(self.KEYS.CANONICAL_MC_DATA)
        raise NotImplementedError(f'Mode not available: {mode}')

    def _on_x_axis_change(self, change):
        if gui.utils.is_value_change(change):
            self._set_axis_type()

    @gui.update_statusbar
    @gui.utils.disable_cls_widget('update_button')
    def _on_update_click(self, b):
        try:
            self._update_plot()
        except Exception as exc:
            logger.error(exc)

    def _update_plot(self):
        # do stuff
        with plt.style.context('seaborn'):
            self._update_emin_plot(self.axes[0])
            self._update_emean_plot(self.axes[1])
            self._update_accept_rate_plot(self.axes[2])
            self._set_axis_type()

        for fig, out in zip(self.figures, self.plot_outputs):
            with out:
                clear_output(wait=True)
                display(fig)

    def _update_emin_plot(self, ax):
        ax.clear()
        # Get plot data
        for run_i, data in enumerate(self.get_data()):
            meta = data['meta']
            natoms = meta['natoms']
            x = np.array(data['temperature'])
            # Normalize energy to eV/atom
            y = np.array(data['emin']) / natoms
            if run_i == 0:
                # Normalize to the first energy point of the first run
                E0 = y[0]
            y -= E0
            # Do the plot
            ax.plot(x, y, 'o--', label=f'Run {run_i+1}')

        if self.invert_temp_axis.value:
            ax.invert_xaxis()  # Temp goes from high->low

        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel(r'$E_{min} - E_0$ (eV/atom)')
        legend = ax.legend(frameon=True)
        # This is a nicer legend color when using the seaborn dark grid
        legend.get_frame().set_facecolor('white')

    def _update_emean_plot(self, ax):
        ax.clear()
        # Get plot data
        for run_i, data in enumerate(self.get_data()):
            meta = data['meta']
            natoms = meta['natoms']
            x = np.array(data['temperature'])
            # Normalize energy to eV/atom
            y = np.array(data['mean_energy']) / natoms
            if run_i == 0:
                # Normalize to the first energy point of the first run
                E0 = y[0]
            y -= E0
            # Do the plot
            ax.plot(x, y, 'o--', label=f'Run {run_i+1}')
        if self.invert_temp_axis.value:
            ax.invert_xaxis()  # Temp goes from high->low
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel(r'$E_{mean} - E_0$ (eV/atom)')
        legend = ax.legend(frameon=True)
        # This is a nicer legend color when using the seaborn dark grid
        legend.get_frame().set_facecolor('white')

    def _update_accept_rate_plot(self, ax):
        ax.clear()
        # Get plot data
        for run_i, data in enumerate(self.get_data()):
            x = np.array(data['temperature'])
            y = np.array(data['accept_rate'])

            # Do the plot
            ax.plot(x, y, 'o--', label=f'Run {run_i+1}')

        if self.invert_temp_axis.value:
            ax.invert_xaxis()

        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Accept rate')
        # Accept rate goes from [0, 1], so add a little extra
        # so the dots stay within the plot
        ax.set_ylim([-0.05, 1.05])
        legend = ax.legend(frameon=True)
        # This is a nicer legend color when using the seaborn dark grid
        legend.get_frame().set_facecolor('white')

    def _set_axis_type(self):
        value = self.x_axis_style_widget.value
        for ax in self.axes:
            ax.set_xscale(value)

    @property
    def active_mc_mode(self):
        return self.mode_widget.value

    def _make_savefig_box(self, fig):
        """Make an hbox with a save figure button and a text field
        to specify the figure name"""
        savefig_button = widgets.Button(description='Save Figure')
        fig_name_text = widgets.Text(description='Filename',
                                     value='figure.png')

        def _on_save_click(b):
            cwd = self.app_data[self.KEYS.CWD]
            fname = str(cwd / fig_name_text.value)

            fig.savefig(fname)
            logger.info('Saved figure to file: %s', fname)

        savefig_button.on_click(_on_save_click)
        # Hbox placing the button and text widget side-by-side
        box = widgets.HBox(children=[savefig_button, fig_name_text])
        return box
