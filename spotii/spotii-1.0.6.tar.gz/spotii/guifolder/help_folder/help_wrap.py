import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
grandparentdir =  os.path.dirname(parentdir)
sys.path.insert(0, grandparentdir)

import title_rc

from whatis_wrap import _Whatis
from play import _Play
from version import version

class _HelpDialog(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_HelpDialog, self).__init__(parent)


        loadUi(os.path.join(currentdir,'help.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setWindowFlags(flags)
        
#        self.exec()

    def closeEvent(self,event):
        print("Pop dialog is closing")

    def config(self):
        try:
            
            self.play_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.whatis.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.more.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.faq_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.legal.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.contact.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
#            QtWidgets.qApp.focusChanged.connect(self.on_focusChanged)

            self.play_button.clicked.connect(self.play_button_hook)
            self.whatis.clicked.connect(self.open_whatis)
            self.more.clicked.connect(self.open_more)
            self.faq_button.clicked.connect(self.open_faq)
            self.legal.clicked.connect(self.open_legal)
            self.contact.clicked.connect(self.open_contact)

            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.close)

            pass
        except Exception as error:
            print(error)

    def open_sub_window(self, title, html_file):
        sub_window = _Whatis(title, html_file)
        sub_window.move(self.geometry().x(), self.geometry().y())
        sub_window.exec()
        
    def open_whatis(self):
        self.open_sub_window('Look Spot II '+version, '/home/pi/app/spotii/launcher/comming.html')
    def open_more(self):
        self.open_sub_window(self.tr('More Information'), '/home/pi/app/spotii/launcher/comming.html')
    def open_faq(self):
        self.open_sub_window(self.tr('FAQ'), '/home/pi/app/spotii/launcher/comming.html')
    def open_legal(self):
        self.open_sub_window(self.tr('Legal Notice and Privacy Policy'), '/home/pi/app/spotii/launcher/legal.html')
    def open_contact(self):
        self.open_sub_window(self.tr('Contact Us'), '/home/pi/app/spotii/launcher/contact.html')

    def play_button_hook(self):
        play_window = _Play()
        play_window.move(0,0)
        play_window.exec()
        
##    def on_focusChanged(self):
##        print('focus changed')

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)

    QtWidgets.QMainWindow
##    drtn=_HelpDialog().exec()
##    print('pop dialog end',drtn)
    window=_HelpDialog()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
