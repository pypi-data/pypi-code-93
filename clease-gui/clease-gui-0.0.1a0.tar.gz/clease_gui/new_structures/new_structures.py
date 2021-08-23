import logging
from IPython.display import display, clear_output
import ipywidgets as widgets
from clease.structgen import NewStructures
from clease_gui import register_logger, BaseDashboard, update_statusbar, utils
from . import StructureGenerationDashboard, GeneralNewStructSettingsDashboard

__all__ = ['NewStructureDashboard']

logger = logging.getLogger(__name__)
register_logger(logger)

# Register the clease structgen logger
logger_clease = logging.getLogger('clease.structgen.new_struct')
register_logger(logger_clease)


class NewStructureDashboard(BaseDashboard):
    """Main dashboard for generating structures"""
    def initialize(self):

        self.general_settings_out = widgets.Output()
        self.structure_gen_out = widgets.Output()

        self.general_new_struct_dashboard = GeneralNewStructSettingsDashboard(
            self.app_data)
        with self.general_settings_out:
            clear_output()
            self.general_new_struct_dashboard.display()

        self.struct_gen_dashboard = StructureGenerationDashboard(self.app_data)
        with self.structure_gen_out:
            clear_output()
            self.struct_gen_dashboard.display()

        self.tab = widgets.Tab(children=[
            self.general_settings_out,
            self.structure_gen_out,
        ])

        self.tab.set_title(0, 'General Settings')
        self.tab.set_title(1, 'Structure Generation')

        # Button for running the new structures generation
        self.generate_widget = widgets.Button(description='Generate',
                                              button_style='primary')
        self.generate_widget.on_click(self._on_generate_click)
        # Make a box which places the button centralized
        box_layout = widgets.Layout(display='flex',
                                    flex_flow='column',
                                    align_items='center',
                                    width='100%')
        self.generate_box = widgets.HBox(children=[self.generate_widget],
                                         layout=box_layout)

    def display(self):
        display(self.tab)
        display(self.generate_box)

    def _make_new_struct_instance(self):
        dash = self.general_new_struct_dashboard  # alias
        generation_number = dash.generation_number
        struct_per_gen = dash.struct_per_gen

        logger.debug('Generation number: %s, struct per gen: %s',
                     generation_number, struct_per_gen)

        settings = self.app_data.get(self.KEYS.SETTINGS, None)
        if settings is None:
            logger.error('Settings does not exist yet.')
            return None

        new_struct = NewStructures(
            settings,
            generation_number=generation_number,
            struct_per_gen=struct_per_gen,
        )
        return new_struct

    def get_generator_settings(self):
        """Collect the args and kwargs from the generation dashboard"""
        dash = self.struct_gen_dashboard  # Alias

        args = dash.get_args()
        kwargs = dash.get_kwargs()
        func_name = dash.get_generator_name()

        return dict(func_name=func_name, args=args, kwargs=kwargs)

    def _generate(self, new_struct, generator_settings):
        """Run the generate function on the new struct class"""
        func_name = generator_settings['func_name']
        args = generator_settings['args']
        kwargs = generator_settings['kwargs']

        # Execute the generation function
        logger.debug('Executing generation function: %s', func_name)
        logger.debug('Generator args: %s', args)
        logger.debug('Generator kwargs: %s', kwargs)
        getattr(new_struct, func_name)(*args, **kwargs)

    @update_statusbar
    def _on_generate_click(self, b):
        try:
            with utils.disable_widget_context(self.generate_widget):
                # Disable the generate more structures button
                self._do_generate()
        except Exception as exc:
            self.log_error(logger, exc)

    def _do_generate(self):
        logger.info('Generating new structures')
        generator_settings = self.get_generator_settings()
        logger.debug('Running with the following settings:\n%s',
                     generator_settings)
        new_struct = self._make_new_struct_instance()
        if new_struct is None:
            logger.error('Failed to make a NewStructures instance.')
            return
        self._generate(new_struct, generator_settings)

        logger.info('Structure generation complete!')
