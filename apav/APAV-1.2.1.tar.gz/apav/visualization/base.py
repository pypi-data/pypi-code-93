"""
This file is part of APAV.

APAV is a python package for performing analysis and visualization on
atom probe tomography data sets.

Copyright (C) 2018 Jesse Smith

APAV is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

APAV is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with APAV.  If not, see <http://www.gnu.org/licenses/>.
"""

from apav.qt import *
from apav.vtkall import *
# from apav.visualization.viewport import Viewer3D
from apav.utils.helpers import make_action
from apav.utils import validate


class BaseVisualization(QMainWindow):
    def __init__(self, ref_data):
        """
        Common model for all visualization classes

        :param ref_data: Miscellaneous data to be referred to by the visualization class, typically a roi or analysis instance
        """
        super().__init__()
        self.ref_data = ref_data
        self.toolbar_actions = []
        self.toolbar = self.addToolBar("Tools")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.setupToolBarActions()

    def makeToolBar(self):
        for i in self.toolbar_actions:
            if isinstance(i, QAction):
                self.toolbar.addAction(i)
            elif isinstance(i, QWidget):
                self.toolbar.addWidget(i)
            elif i is None:
                self.toolbar.addSeparator()

    def setupToolBarActions(self):
        tb = self.toolbar_actions
        tb.append(make_action("Save as image", self.exportImage, icon="saveas.svg"))
        tb.append(make_action("Copy as image", self.copyImage, icon="copy.svg"))
        tb.append(make_action("Save as raw data", self.exportRawData, icon="export.svg"))
        self.toolbar.addSeparator()

    def exportImage(self):
        path, filter = QFileDialog.getSaveFileName(self, "Save as png", filter="*.png")
        if not path:
            return

        widg = self.centralWidget()
        pix = QPixmap(widg.size())
        widg.render(pix)
        pix.save(path, "png", 100)

    def copyImage(self):
        widg = self.centralWidget()
        pix = QPixmap(widg.size())
        widg.render(pix)
        QApplication.clipboard().setPixmap(pix)

    def exportRawData(self):
        raise validate.AbstractMethodError()


class PyQtGraphVisualization(BaseVisualization):
    def __init__(self):
        super().__init__()


# class VTKVisualization(BaseVisualization):
#     def __init__(self):
#         super().__init__()
#         self.viewport = Viewer3D(self)
#         self.setCentralWidget(self.viewport)
#         self.viewport.initialize()


