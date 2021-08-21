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


# class AxesIndicator(vtkAxesActor):
#     """
#     VTK widget for displaying axes indicators in corner of screen
#     """
#     def __init__(self, iren):
#         super().__init__()
#         # super(AxesIndicator, self).__init__(iren)
#         self._axesWidget = vtkOrientationMarkerWidget()
#         self._axesWidget.SetOutlineColor(0.5, 0.5, 0.5)
#         self._axesWidget.SetOrientationMarker(self)
#         self._axesWidget.SetInteractor(iren)
#         self._axesWidget.SetViewport(0.0, 0, 0.15, 0.2)
#         self._axesWidget.SetEnabled(1)
#         self._axesWidget.InteractiveOff()
#         self.SetXAxisLabelText("x")
#         self.SetYAxisLabelText("y")
#         self.SetZAxisLabelText("z")
#
#         x = self.GetXAxisCaptionActor2D().GetTextActor()
#         y = self.GetYAxisCaptionActor2D().GetTextActor()
#         z = self.GetZAxisCaptionActor2D().GetTextActor()
#         txt = [x, y, z]
#         for i in txt:
#             i.SetMinimumSize(15, 15)
#             prop = i.GetTextProperty()
#             prop.SetColor(0, 0, 0)
#             prop.ShadowOff()
#             prop.ItalicOff()
#
#
# class VTKWidget(QVTKRenderWindowInteractor):
#     def __init__(self):
#         super().__init__()
#         self.setCursor(QCursor(Qt.OpenHandCursor))
#
#     def mousePressEvent(self, event):
#         """
#         Use the correct cursor for the mouse operation
#         """
#         btn = event.button()
#         if btn == 1:
#             QApplication.setOverrideCursor(QCursor(Qt.ClosedHandCursor))
#         elif btn == 4:
#             QApplication.setOverrideCursor(QCursor(Qt.SizeAllCursor))
#         elif btn == 2:
#             QApplication.setOverrideCursor(QCursor(Qt.SizeVerCursor))
#         super().mousePressEvent(event)
#
#     def mouseReleaseEvent(self, event):
#         """
#         Restore the cursor after operation is complete
#         """
#         QApplication.restoreOverrideCursor()
#         super().mouseReleaseEvent(event)
#
#
# class Viewer3D(QGLWidget):
#     """
#     Viewer for displaying 3D data
#     """
#     def __init__(self, window):
#         super().__init__()
#
#         self.window = window
#
#         # Layout
#         self._layout = QVBoxLayout()
#         self._layout.setContentsMargins(0, 0, 0, 0)
#         self._vtkwidget = VTKWidget()
#         self._layout.addWidget(self._vtkwidget)
#         self.setLayout(self._layout)
#
#         self._ren = vtkOpenGLRenderer()
#
#         # Camera
#         self._camera = self._ren.MakeCamera()
#         self._camera.SetParallelProjection(True)
#         self._camera.SetPosition(-1, 0, 0)
#         self._camera.SetViewUp(0, 0, 1)
#         self._camera.SetViewAngle(180)
#         self._ren.SetActiveCamera(self._camera)
#
#         self.clipping_range = self._camera.GetClippingRange()
#
#         # Render window
#         self._renwin = self._vtkwidget.GetRenderWindow()
#         self._renwin.StereoCapableWindowOff()
#         self._renwin.AddRenderer(self._ren)
#         self._renwin.LineSmoothingOn()
#         self._renwin.PointSmoothingOn()
#         self._ren.SetBackground(1, 1, 1)
#
#         # Interactor
#         self._iren = self._renwin.GetInteractor()
#         self._iren.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
#
#         # Create axes indicators in bottom left of screen
#         self._axes = AxesIndicator(self._iren)
#         self.antialiasing(True)
#
#     def initialize(self):
#         self._iren.Initialize()
#         self.zoom_all()
#
#     def register_actors(self, actor):
#         """
#         Add actor(s) to renderer appropriately
#         """
#         if hasattr(actor, "__iter__"):
#             for act in actor:
#                 self.register_actors(act)
#         else:
#             # Some actors need objects from rendering objects, we do that here
#             if isinstance(actor, vtkFollower):
#                 actor.SetCamera(self._camera)
#             elif isinstance(actor, vtkCubeAxesActor):
#                 actor.SetCamera(self._camera)
#
#             self._ren.AddActor(actor)
#         self.zoom_all()
#
#     def reload(self):
#         """
#         Reload the viewer
#         """
#         self._ren.RemoveAllViewProps()
#         for actor in self.form.actors:
#             self.register_actors(actor)
#
#         self._camera.SetViewAngle(self.form.structure["perspective_projection_view_angle"])
#         self.force_render()
#
#     def force_render(self):
#         """
#         Force the render/update/repaint of the viewport
#         """
#         self._camera.Render(self._ren)
#         self._vtkwidget.update()
#
#     def default_interactor(self):
#         """
#         Reset the interactor to vtkInteractorStyleTrackballCamera
#         """
#         self._iren.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
#
#     def zoom_all(self):
#         self._ren.ResetCamera()
#         self.force_render()
#
#     def antialiasing(self, val):
#         assert type(val) == bool
#         self._ren.SetUseFXAA(val)
#
#     def save_screenshot(self, filepath):
#         """
#         Save a screenshot of the render window
#         """
#         # If the file path string does not have .png add it
#         if not filepath[-4:].lower() == ".png":
#             filepath += ".png"
#
#         # Do the export
#         img = vtkWindowToImageFilter()
#         img.SetInput(self._renwin)
#         writer = vtkPNGWriter()
#         writer.SetInputConnection(img.GetOutputPort())
#         writer.SetFileName(filepath)
#         self._renwin.Render()
#         writer.Write()
#
#     def rotate(self, kind, value):
#         """
#         Rotate the view in roll, yaw, or pitch modes
#         """
#         if kind == "roll":
#             self._camera.Roll(value)
#         elif kind == "yaw":
#             self._camera.Azimuth(value)
#         elif kind == "pitch":
#             self._camera.Elevation(value)
#         self.force_render()
#
#     def mesh_viewall(self, kind):
#         if kind == "wireframe":
#             for actor in self._ren.actors():
#                 actor.GetProperty().SetRepresentationToWireFrame()
#
#     def parallel_projection(self, value):
#         self._camera.SetParallelProjection(value)
#         self.force_render()
