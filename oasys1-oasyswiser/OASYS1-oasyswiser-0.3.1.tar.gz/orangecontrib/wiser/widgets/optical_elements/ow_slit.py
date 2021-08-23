import numpy

from syned.widget.widget_decorator import WidgetDecorator
from syned.beamline.shape import Plane
from orangewidget.settings import Setting

from LibWiser import Optics

from wofrywiser.beamline.beamline_elements import WiserOpticalElement

from orangecontrib.wiser.widgets.gui.ow_optical_element import OWOpticalElement
from orangecontrib.wiser.widgets.gui.ow_wise_widget import PositioningDirectivesPhrases

class OWSlits(OWOpticalElement, WidgetDecorator):
    name = "Slits"
    id = "Slits"
    description = "Slits"
    icon = "icons/slit.png"
    priority = 1

    length = Setting(0.01)
    alpha = Setting(90.0)

    oe_name = Setting("Slit")

    def after_change_workspace_units(self):
        super(OWSlits, self).after_change_workspace_units()

    def build_mirror_specific_gui(self, container_box):
        pass

    def get_native_optical_element(self):
        return Optics.Slits(L=self.length)

    def get_optical_element(self, native_optical_element):
         return WiserOpticalElement(name=self.oe_name,
                                    boundary_shape=None,
                                    native_CoreOptics=native_optical_element,
                                    native_PositioningDirectives=self.get_PositionDirectives())


    def receive_specific_syned_data(self, optical_element):
        pass

    def check_syned_shape(self, optical_element):
        if not isinstance(optical_element._surface_shape, Plane):
            raise Exception("Syned Data not correct: Mirror Surface Shape is not Elliptical")

from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
import sys

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWSlits()
    ow.show()
    a.exec_()
    ow.saveSettings()