from IPython.display import display
import ipywidgets as widgets
from clease_gui import BaseDashboard, utils

__all__ = ['GeneralNewStructSettingsDashboard']


class GeneralNewStructSettingsDashboard(BaseDashboard):
    # Automatically determine generation number by default?
    DEFAULT_AUTO_GEN = True

    def initialize(self):

        # Generation number box
        # None = automatically figure it out, add a checkbox for this
        self.gen_int_b = widgets.BoundedIntText(
            value=0,
            min=0,
            max=9999999,
            # We disable this box if we check figuring it out automatically
            disabled=self.DEFAULT_AUTO_GEN,
            description='Generation number:',
            **self.DEFAULT_STYLE_KWARGS,
        )
        self.gen_auto_b = widgets.Checkbox(
            value=self.DEFAULT_AUTO_GEN,
            description='Automatically determine generation number?',
            **self.DEFAULT_STYLE_KWARGS)

        def on_gen_auto_change(change):
            """Disable the gen_int_b widget if we enable automatic
            generation ID determination"""
            if utils.is_value_change(change):
                self.gen_int_b.disabled = change['new']

        self.gen_auto_b.observe(on_gen_auto_change)

        self.gen_b = widgets.HBox(children=[self.gen_int_b, self.gen_auto_b])

        # Box for number of structures per generation
        self.struct_per_gen_b = widgets.BoundedIntText(
            value=5,
            min=1,
            max=9999999,
            description='No. struct per gen:',
            **self.DEFAULT_STYLE_KWARGS,
        )

    def display(self):
        display(self.gen_b, self.struct_per_gen_b)

    @property
    def generation_number(self):
        if self.gen_auto_b.value is True:
            # This uses the automatic determination
            return None
        return self.gen_int_b.value

    @property
    def struct_per_gen(self):
        return self.struct_per_gen_b.value
