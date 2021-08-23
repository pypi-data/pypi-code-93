from PySide6 import QtGui, QtOpenGLWidgets
from PySide6.QtCore import Qt
from PySide6.QtOpenGL import *


class OpenGLWidget(QtOpenGLWidgets.QOpenGLWidget, QtGui.QOpenGLFunctions):

    def surface_format():
        format = QtGui.QSurfaceFormat()
        format.setDepthBufferSize(0)
        format.setStencilBufferSize(0)
        format.setVersion(3, 2)
        format.setProfile(QtGui.QSurfaceFormat.CoreProfile)
        return format

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFormat(OpenGLWidget.surface_format())
        self.width = parent.size().width() if parent else 1920
        self.height = parent.size().height() if parent else 1080
        frame = QtGui.QImage(self.width, self.height, QtGui.QImage.Format_RGB888)
        frame.fill(Qt.white)
        self.frame = frame

    def new_frame(self, frame):
        self.frame = frame
        self.paintGL()

    def initializeGL(self):
        texture = QOpenGLTexture(self.frame)
        texture.create()

    def paintGL(self):
        texture = QOpenGLTexture(self.frame)
        texture.create()
        texture.bind()

    def resizeGL(self, width, height):
        f = self.context().extraFunctions()
        f.glViewport(0, 0, width, height)
