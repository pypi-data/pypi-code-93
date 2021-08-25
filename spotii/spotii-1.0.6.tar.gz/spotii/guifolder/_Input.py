import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from define import *
import title_rc
from main_paras import getMainTopLeft
import main_paras
from vkeyboard import handleVisibleChanged

class _Input(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(_Input, self).__init__(parent)
        
        self.original = True
        self.last_scroll_value=0
        loadUi(os.path.join(currentdir,'input.ui'),self)
        #self.setStyleSheet('.QWidget{background-image: url(:/public/png/public/rectangle.png);border:0px;}')
        self.setStyleSheet('background-color: rgb(5, 11, 126)')
        self.config()
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        


    def keyUp(self):
        print('keyUp got emit')
        if self.original:
            self.original = False
            self.scroll.setVisible(True)
            self.move(0,0)
            self.repaint()
        
    def closeEvent(self,event):
        print("_CreateAccount is closing")

    def config(self):
        try:

            self.scroll.setMaximum(20)
            self.scroll.valueChanged.connect(self.scrolled)
            self.scroll.hide()
            main_paras.keyboard_up.signal.connect(self.keyUp)
            
            pass
        except Exception as error:
            print(error)

    def scrolled(self):
        try:
            diff =(self.last_scroll_value - self.scroll.value())*10
            self.last_scroll_value=self.scroll.value()
            print(self.scroll.value())
            children= self.widget.findChildren(QtWidgets.QWidget)
            for child in children:
                if child != self.scroll:
                    child.move(child.pos().x(),child.pos().y()+diff)
            self.repaint()
        except Exception as error:
            print(error)

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
    
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)

    QtWidgets.QMainWindow
    window=_Input()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
