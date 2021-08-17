from PyQt5.QtWidgets import QLabel
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import *
import sys

class TeraAppWIcon:
  def __init__(self, title, x, y, icon, colorbg):
    self.app = QtWidgets.QApplication(sys.argv)
    self.win = QtWidgets.QMainWindow()
    self.win.setWindowTitle(title)
    self.win.setGeometry(500, 200, x, y)
    self.win.setWindowIcon(QIcon(icon))
    self.win.setStyleSheet(f"background-color: {colorbg};")

    self.win.show()


  def txt(self,txt, x, y, size):
    self.txt_name = QtWidgets.QLabel(self.win)
    self.txt_name.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    self.txt_name.resize(400,70)
    self.txt_name.setText(txt)
    self.txt_name.move(x, y)
    self.txt_name.setFont(QFont('Arial', size))
    self.txt_name.setStyleSheet(f"background-color: none")
    self.txt_name.show()

  def txtc(self,txt, x, y, size, color):
    self.txtc_name = QtWidgets.QLabel(self.win)
    self.txtc_name.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    self.txtc_name.resize(400,70)
    self.txtc_name.setText(txt)
    self.txtc_name.move(x, y)
    self.txtc_name.setFont(QFont('Arial', size))
    self.txtc_name.setStyleSheet(f"color: {color}; background-color: none")
    self.txtc_name.show()

  def button(self, txt, x, y, colorbg):
    self.button_name = QtWidgets.QPushButton(self.win)
    self.button_name.setText(txt)
    self.button_name.move(x,y)
    self.button_name.setStyleSheet(f"background-color: {colorbg};")
    self.button_name.show()

  def buttonf(self, txt, x, y, colorbg, function):
    self.buttonf_name = QtWidgets.QPushButton(self.win)
    self.buttonf_name.setText(txt)
    self.buttonf_name.move(x, y)
    self.buttonf_name.setStyleSheet(f"background-color: {colorbg};")
    self.buttonf_name.clicked.connect(function)
    self.buttonf_name.show()

  def buttonfr(self, txt, x, y, colorbg, function, size_x, size_y):
    self.buttonfr_name = QtWidgets.QPushButton(self.win)
    self.buttonfr_name.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    self.buttonfr_name.resize(size_x,size_y)
    self.buttonfr_name.setText(txt)
    self.buttonfr_name.move(x, y)
    self.buttonfr_name.setStyleSheet(f"background-color: {colorbg};")
    self.buttonfr_name.clicked.connect(function)
    self.buttonfr_name.show()

  def img(self, img, x, y, size_x, size_y):
    img_name = QtWidgets.QLabel(self.win)
    img_name.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    img_name.resize(size_x,size_y)
    img_name.setContentsMargins(0,0,0,0)
    pixmap = QtGui.QPixmap(f'{img}')
    img_name.setPixmap(pixmap)
    img_name.setMinimumSize(1,1)
    layout_name = QtWidgets.QVBoxLayout()
    layout_name.addWidget(img_name)
    img_name.move(x, y)
    img_name.show()

  def icon(self, img, x, y):
    im = QPixmap(f"{img}").scaledToHeight(36)
    self.icon_name = QLabel(self.win)
    self.icon_name.setPixmap(im)
    self.icon_name.move(x, y)
    self.icon_name.show()

  def input(self, x, y, colorbg):
    self.input_name = QtWidgets.QLineEdit(self.win)
    self.input_name.move(x, y)
    self.input_name.setStyleSheet(f"background-color: {colorbg};")
    self.input_name.show()

  def inputr(self, x, y, colorbg, size_x, size_y):
    self.inputr_name = QtWidgets.QLineEdit(self.win)
    self.inputr_name.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    self.inputr_name.resize(size_x,size_y)
    self.inputr_name.move(x, y)
    self.inputr_name.setStyleSheet(f"background-color: {colorbg};")
    self.inputr_name.show()

  def sidebar(self,colorbg, size_x):
    self.sidebar_name = QtWidgets.QLabel(self.win)
    self.sidebar_name.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    self.sidebar_name.resize(size_x, 2500)
    self.sidebar_name.setStyleSheet(f"background-color: {colorbg};")
    self.sidebar_name.show()


  def appbar(self,colorbg, size_y):
    self.sidebar_name = QtWidgets.QLabel(self.win)
    self.sidebar_name.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    self.sidebar_name.resize(2500, size_y)
    self.sidebar_name.setStyleSheet(f"background-color: {colorbg};")
    self.sidebar_name.show()






















