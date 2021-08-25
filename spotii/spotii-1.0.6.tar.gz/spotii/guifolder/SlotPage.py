import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import title_rc
#from main_paras import mainChannelNotify, getDetectionMode, setOperation
from main_paras import getDetectionMode, setOperation
from define import *


class SlotPage(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(SlotPage, self).__init__(parent)

        loadUi(os.path.join(currentdir,'slotPage.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        self.resize(96, 224)
        self.slot =0
        self.page =0
    def setDetail(self,slot,page):
        try:
            self.slot=slot+1
            self.page=page
            if self.page>=SLOT_STATUS_DETECTING and self.page<=SLOT_STATUS_INVALID :
                self.button.hide()
                self.number.setText(str(self.slot))
                if self.page != SLOT_STATUS_DETECTING:
                    #print('hide timer')
                    self.timer.hide()
            elif self.page>=SLOT_STATUS_SCAN and self.page<=SLOT_STATUS_INVALID_QR :
                self.id.hide()
                self.timer.hide()
                self.button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            else:
                self.id.hide()
                self.timer.hide()
                self.button.hide()
                
        except Exception as error:
            print(error)
    def buttonHook(self, hookFunction):
        if hookFunction!=None:
            self.button.clicked.connect(hookFunction)
    def config(self):
        try:
            #self.id.lower()
            #self.timer.lower()
            
            pass
        except Exception as error:
            print(error)
            
    def button_click(self):
        try:
            print('slot', self.slot, 'page', self.page)
            setOperation(self.slot-1, self.page)
                
        except Exception as error:
            print(error)


if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)

    QtWidgets.QMainWindow
    window=SlotPage()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
