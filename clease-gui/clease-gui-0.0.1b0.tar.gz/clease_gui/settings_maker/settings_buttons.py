import logging
from abc import ABC
from IPython.display import display, clear_output
import ipywidgets as widgets
import numpy as np
import clease_gui as gui
from clease_gui.widget_collection import WidgetCollection, SingleWidget

logger = logging.getLogger(__name__)
gui.register_logger(logger)


class MaxClusterDiaWidget(SingleWidget):
    """Special widget for max cluster diameters, it needs to update itself,
    and recreate the VBox every time it needs to update."""
    DEFAULT_MCD_VALUE = 5.0

    def __init__(self, name, num_boxes, priority=0):
        self.mcd_boxes = []
        self.label = widgets.Label(
            value='Max cluster diameter:',
            # # layout=self.widget.layout,
            # display='flex',
            # flex_flow='column',
        )

        # Update the number of boxes, and create the initial widget
        self._update_boxes(num_boxes)
        initial_widget = self.make_widget()
        super().__init__(name, initial_widget, priority=priority)
        # The output object we will be drawing the MCD object on
        self.output = widgets.Output()

    def make_widget(self):
        return widgets.VBox(children=self.mcd_boxes)

    def update_widget(self, num_boxes):
        self._update_boxes(num_boxes)
        self.widget = self.make_widget()
        # The output has already been displayed, so it doesn't need to be updated
        self.display_widget(display_output=False)

    @property
    def value(self):
        # Return a NumPy array with the MCD values
        return np.array([child.value for child in self.widget.children])

    def _update_boxes(self, num_boxes):
        def add_box():
            """Helper function for making a bound float box"""
            i = len(self.mcd_boxes)
            box = widgets.BoundedFloatText(
                description=f'{i+2}-body',
                value=self.DEFAULT_MCD_VALUE,
                min=0,
                disabled=False,
            )
            self.mcd_boxes.append(box)

        delta = len(self.mcd_boxes) - num_boxes

        if delta > 0:
            # We have more boxes than MCS, pop the difference
            for _ in range(delta):
                try:
                    self.mcd_boxes.pop()
                except IndexError:
                    # mcd_boxes is empty, no need to continue
                    break
        elif delta < 0:
            # We need to add boxes
            for _ in range(abs(delta)):
                add_box()
        logger.debug('Number of boxes in MCD object: %s', len(self.mcd_boxes))

    def set_value(self, value):
        if not len(value) == len(self.mcd_boxes):
            raise ValueError('Incorrect length of value. Got {}, expected {}',
                             len(value), len(self.mcd_boxes))
        for ii, val in enumerate(value):
            self.mcd_boxes[ii].value = val

    def display_widget(self, display_output=True):
        """Display the widget.

        :param display_output: call display() on the output oject.
            Should only be True on the first call, to avoid repeated objects, unless it needs
            to be redrawn after a clear_output()
        """
        with self.output:
            # We are the only ones drawing in this output,
            # so we always clear on an update
            clear_output(wait=True)
            vbox = widgets.VBox(children=[self.label, self.widget])
            vbox.layout.align_items = 'center'
            display(vbox)
            # display(self.label)
            # display(self.widget)
        if display_output:
            logger.debug('Drawing mcd widget output')
            # We don't always want to redraw the entire output, e.g. when simply redrawing
            # this widget in its own output
            display(self.output)


class MaxClusterWidget(WidgetCollection):
    """Widget for doing max cluster size and max cluster diameter"""
    MAX_CLUSTER_SIZE_NAME = 'max_cluster_size'
    MAX_CLUSTER_DIA_NAME = 'max_cluster_dia'

    def make_widgets(self):
        widget_lst = []

        self._max_cluster_output = widgets.Output()
        # Max cluster size and max cluser diameter
        self.max_cluster_size = widgets.BoundedIntText(
            value=4,
            min=2,
            description='Max cluster size:',
            **self.DEFAULT_STYLE_KWARGS,
        )

        widget_lst.append(
            SingleWidget(self.MAX_CLUSTER_SIZE_NAME,
                         self.max_cluster_size,
                         priority=10))

        self.mcd_widget = MaxClusterDiaWidget(self.MAX_CLUSTER_DIA_NAME,
                                              self.number_of_boxes(),
                                              priority=9)

        widget_lst.append(self.mcd_widget)

        def on_max_cluster_size_change(change):
            if gui.utils.is_value_change(change):
                self.update_mcd_widget()

        self.max_cluster_size.observe(on_max_cluster_size_change)
        return widget_lst

    def update_mcd_widget(self):
        logger.debug('Updating mcd widget')
        self.mcd_widget.update_widget(self.number_of_boxes())

    def number_of_boxes(self):
        """Helper function which calculates how many MCD
        # boxes we should have"""
        return self.max_cluster_size.value - 1

    def display_single_widget(self, widget: SingleWidget):
        # Display the max cluster dia and max cluster size widget together
        if widget.name == self.MAX_CLUSTER_SIZE_NAME:
            # We display both when calling max_cluster_dia
            return
        if widget.name == self.MAX_CLUSTER_DIA_NAME:
            box = widgets.HBox(
                children=[self.max_cluster_size, self.mcd_widget.output])
            box.layout.align_items = 'baseline'
            self.mcd_widget.display_widget(display_output=False)
            with self._max_cluster_output:
                clear_output()
                display(box)
            display(self._max_cluster_output)
            return
        super().display_single_widget(widget)

    def get_max_cluster_size(self):
        return self.max_cluster_size.value

    def set_widget_value(self, key, value):
        if key == 'max_cluster_size':
            self.max_cluster_size.value = value
            self.update_mcd_widget()
        elif key == 'max_cluster_dia':
            self.mcd_widget.set_value(value)
        else:
            super().set_widget_value(key, value)


class CommonSettingsButtons(MaxClusterWidget, WidgetCollection, ABC):
    """Some buttons which are shared between all the CLEASE settings types,
    most notably the max cluster dia and max cluster size"""
    def __init__(self, app_data, *args, **kwargs):
        # Store the FloatBoxes for the max cluster dia array
        self.app_data = app_data
        super().__init__(*args, **kwargs)

    def make_widgets(self):
        widget_lst = super().make_widgets()

        # Basis func type
        basis_func_type = widgets.Dropdown(
            options=[('Polynomial', 'polynomial'),
                     ('Trigonometric', 'trigonometric'),
                     ('Binary Linear', 'binary_linear')],
            description='Basis function:',
            **self.DEFAULT_STYLE_KWARGS,
        )
        widget_lst.append(
            SingleWidget('basis_func_type', basis_func_type, priority=100))

        # include background atoms
        include_background_atoms = widgets.Dropdown(
            options=[('True', True), ('False', False)],
            value=False,
            description='Background atoms:',
            **self.DEFAULT_STYLE_KWARGS,
        )
        widget_lst.append(
            SingleWidget('include_background_atoms',
                         include_background_atoms,
                         priority=5))

        # db_name
        db_name = widgets.Text(
            value='clease.db',
            description='Database name:',
            **self.DEFAULT_STYLE_KWARGS,
        )
        widget_lst.append(SingleWidget('db_name', db_name, priority=1))
        return widget_lst

    def get_widget_value(self, widget: SingleWidget):
        if widget.name == 'db_name':
            # Add the cwd to the database name
            # cwd = self.app_data[gui.AppDataKeys.CWD]
            # return str(cwd / widget.widget.value)
            return widget.widget.value
        return super().get_widget_value(widget)


class CEBulkButtons(CommonSettingsButtons):
    def make_widgets(self):
        widget_list = super().make_widgets()

        crystalstructure = widgets.Dropdown(
            options=[
                ('Simple Cubic', 'sc'),
                ('FCC', 'fcc'),
                ('BCC', 'bcc'),
                ('HCP', 'hcp'),
                ('Diamond', 'diamond'),
                ('Zincblende', 'zincblende'),
                ('Rocksalt', 'rocksalt'),
                ('Cesium Chloride', 'cesiumchloride'),
                ('Fluorite', 'fluorite'),
                ('Wurtzite', 'wurtzite'),
            ],
            description='Crystal Structure:',
            **self.DEFAULT_STYLE_KWARGS,
        )

        a = widgets.BoundedFloatText(
            value=None,
            min=0,
            max=999,
            description='a:',
            description_tooltip=(
                'Setting the value to 0 corresponds to setting it to None'),
            **self.DEFAULT_STYLE_KWARGS,
        )

        c = widgets.BoundedFloatText(
            value=None,
            min=0,
            max=999,
            description='c:',
            description_tooltip=(
                'Setting the value to 0 corresponds to setting it to None'),
            **self.DEFAULT_STYLE_KWARGS,
        )

        covera = widgets.BoundedFloatText(
            value=None,
            min=0,
            max=999,
            description='c/a:',
            description_tooltip=(
                'Setting the value to 0 corresponds to setting it to None'),
            **self.DEFAULT_STYLE_KWARGS,
        )

        widget_list.extend([
            SingleWidget('crystalstructure', crystalstructure, priority=80),
            SingleWidget('a', a, priority=75),
            SingleWidget('c', c, priority=70),
            SingleWidget('covera', covera, priority=65),
        ])
        return widget_list

    def get_widget_value(self, widget: SingleWidget):
        """Helper function for getting the value from a button."""
        if widget.name in ['a', 'c', 'covera']:
            # Set value to 0 to ignore
            value = widget.widget.value
            if value == 0:
                return None
        return super().get_widget_value(widget)


class CECrystalButtons(CommonSettingsButtons):
    def make_widgets(self):
        widget_list = super().make_widgets()
        spacegroup = widgets.IntText(
            value=1,
            description='Spacegroup:',
            **self.DEFAULT_STYLE_KWARGS,
        )

        widget_list.append(SingleWidget('spacegroup', spacegroup, priority=80))
        return widget_list


class CESlabButtons(CommonSettingsButtons):
    def make_widgets(self):
        widget_list = super().make_widgets()

        millers = []
        coord = ['x', 'y', 'z']
        for c in coord:
            millers.append(
                widgets.IntText(
                    value=4,
                    description=f'Miller ({c}):',
                    **self.DEFAULT_STYLE_KWARGS,
                ))
        miller_box = widgets.VBox(children=millers)

        widget_list.append(SingleWidget('miller', miller_box, priority=80))
        return widget_list

    def get_widget_value(self, widget: SingleWidget):
        """Helper function for getting the value from a button."""
        if widget.name == 'miller':
            value = np.zeros(3)
            wdgt = widget.widget
            for ii in range(3):
                value[ii] = wdgt.children[ii].value
            return value
        return super().get_widget_value(widget)


class FixedSizeMode(WidgetCollection):
    def make_widgets(self):
        widgets_list = []
        self.cell_size = widgets.Text(
            description='Cell size:',
            value='3, 3, 3',
            **self.DEFAULT_STYLE_KWARGS,
        )

        label_msg = """Example: "1, 2, 3" for (1, 2, 3) or "3" for (3, 3, 3). """
        label = widgets.Label(value=label_msg)

        box = widgets.HBox(children=[self.cell_size, label])

        widgets_list.append(SingleWidget('size', box))
        return widgets_list

    def get_widget_value(self, widget: SingleWidget):
        if widget.name == 'size':
            cell_widget = widget.widget.children[0]
            return self._parse_text(cell_widget.value)
        return super().get_widget_value(widget)

    def _parse_text(self, text):
        orig_text = str(text)
        text = text.strip()
        text = text.replace(',', ' ')
        parts = text.split()
        if len(parts) == 1:
            rep = int(parts[0])
            return tuple(rep for _ in range(3))
        elif len(parts) == 3:
            return tuple(map(int, parts))
        else:
            raise ValueError(
                'Cannot determine size from string: {}'.format(orig_text))

    def set_widget_value(self, key, value):
        if key == 'size':
            self.cell_size.value = value
        else:
            super().set_widget_value(key, value)


class SupercellFactorSizeMode(WidgetCollection):
    def make_widgets(self):
        widgets_list = []
        supercell_factor = widgets.BoundedIntText(
            description='Supercell Factor:',
            value=27,
            min=0,
            max=999,
            **self.DEFAULT_STYLE_KWARGS)

        widgets_list.append(
            SingleWidget('supercell_factor', supercell_factor, priority=50))

        skew_threshold = widgets.BoundedIntText(
            description='Skew Treshold:',
            value=40,
            min=0,
            max=999,
            **self.DEFAULT_STYLE_KWARGS,
        )
        widgets_list.append(
            SingleWidget('skew_threshold', skew_threshold, priority=50))
        return widgets_list
