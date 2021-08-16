from PyQt5.QtWidgets import QLabel
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import *
import sys


class TeraApp:
  def __init__(self, title, x, y, colorbg):
    self.app = QtWidgets.QApplication(sys.argv)
    self.win = QtWidgets.QMainWindow()
    self.win.setWindowTitle(title)
    self.win.setGeometry(500, 200, x, y)
    self.win.setStyleSheet(f"background-color: {colorbg};")

    self.win.show()


  def txt(self,txt, x, y, size):
    self.txt = QtWidgets.QLabel(self.win)
    self.txt.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    self.txt.resize(400,70)
    self.txt.setText(txt)
    self.txt.move(x, y)
    self.txt.setFont(QFont('Arial', size))
    self.txt.show()

  def txtc(self,txt, x, y, size, color):
    self.txtc = QtWidgets.QLabel(self.win)
    self.txtc.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    self.txtc.resize(400,70)
    self.txtc.setText(txt)
    self.txtc.move(x, y)
    self.txtc.setFont(QFont('Arial', size))
    self.txtc.setStyleSheet(f"color: {color}")
    self.txtc.show()

  def inputr(self, x, y, colorbg, size_x, size_y):
    self.inputr = QtWidgets.QLineEdit(self.win)
    self.inputr.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    self.inputr.resize(size_x,size_y)
    self.inputr.move(x, y)
    self.inputr.setStyleSheet(f"background-color: {colorbg};")
    self.inputr.show()

  def input(self, x, y, colorbg):
    self.input_name = QtWidgets.QLineEdit(self.win)
    self.input_name.move(x, y)
    self.input_name.setStyleSheet(f"background-color: {colorbg};")
    self.input_name.show()

  def button(self, txt, x, y, colorbg):
    self.button = QtWidgets.QPushButton(self.win)
    self.button.setText(txt)
    self.button.move(x,y)
    self.button.setStyleSheet(f"background-color: {colorbg};")
    self.button.show()

  def buttonfr(self, txt, x, y, colorbg, function, size_x, size_y):
    self.buttonfr = QtWidgets.QPushButton(self.win)
    self.buttonfr.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    self.buttonfr.resize(size_x,size_y)
    self.buttonfr.setText(txt)
    self.buttonfr.move(x, y)
    self.buttonfr.setStyleSheet(f"background-color: {colorbg};")
    self.buttonfr.clicked.connect(function)
    self.buttonfr.show()

  def buttonf(self, txt, x, y, colorbg, function):
    self.buttonf = QtWidgets.QPushButton(self.win)
    self.buttonf.setText(txt)
    self.buttonf.move(x, y)
    self.buttonf.setStyleSheet(f"background-color: {colorbg};")
    self.buttonf.clicked.connect(function)
    self.buttonf.show()

  def img(self, img, x, y, size_x, size_y):
    label = QtWidgets.QLabel(self.win)
    label.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    label.resize(size_x,size_y)
    label.setContentsMargins(0,0,0,0)
    pixmap = QtGui.QPixmap(f'{img}')
    label.setPixmap(pixmap)
    label.setMinimumSize(1,1)
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(label)
    label.move(x, y)
    label.show()

  def icon(self, img, x, y):
    im = QPixmap(f"{img}").scaledToHeight(36)
    self.icon = QLabel(self.win)
    self.icon.setPixmap(im)
    self.icon.move(x, y)
    self.icon.show()

  def input_get(self):
    self.input_name.text()







