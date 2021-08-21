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

import sys

from apav.qt import *
import apav.visualization.plotting as plot
# from apav.visualization.base import VTKVisualization


obj_map = {
    "mass_spectrum_plot": plot.MassSpectrumPlot,
    "mass_spectrum_plot_ranged": plot.MassSpectrumPlotRanged,
    "mass_spectrum_plot_noise_corrected": plot.MassSpectrumPlotNoiseCorrected,
    "mass_spectrum_plot_local_bkg_corrected": plot.MassSpectrumPlotLocalBkgCorrected,
    "interactive_correlation_histogram_plot": plot.InteractiveCorrelationHistogramPlot,
    # "dead_zone_plot": plot.DetectorDeadZonePlot
}

QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

app = QApplication(sys.argv)
if sys.platform == "win32":
    pal = app.palette()
    app.processEvents()
    pal.setColor(QPalette.Window, Qt.white)
    pal.setColor(QPalette.Background, Qt.white)
    pal.setColor(QPalette.Base, Qt.white)
    app.setPalette(pal)


class VisFactory:
    active = []

    def make(self, typ, *args, **kwargs):
        widget = obj_map[typ](*args, **kwargs)
        return widget


vfactory = VisFactory()
