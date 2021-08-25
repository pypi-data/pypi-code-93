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
g_g_parentdir = os.path.dirname(grandparentdir)
sys.path.insert(0, g_g_parentdir)

import title_rc
from main_paras import getMainTopLeft
from main_paras import api_result_que

import main_paras
from define import *
#from create_new_account import _CreateAccount
import create_new_account
import forgot_password
import test_info
import wrong_password

class _SignIn(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_SignIn, self).__init__(parent)

        loadUi(os.path.join(currentdir,'sign_in.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setWindowFlags(flags)
        self.original = True        

    def keyUp(self):
        print('keyUp got emit')
        if self.original:
            self.original = False
            self.move(0,0)
            self.repaint()

    def config(self):
        try:
            main_paras.keyboard_up.signal.connect(self.keyUp)
            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.close)
            self.create_account.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.sign_in_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.forgot_psw.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            
            self.create_account.clicked.connect(self.create_account_hook)
            self.sign_in_bt.clicked.connect(self.sign_in_bt_hook)
            self.forgot_psw.clicked.connect(self.forgot_psw_hook)
            
            main_paras.keyboard_up.signal.connect(self.keyUp)

            pass
        except Exception as error:
            print(error)

    def create_account_hook(self):
        try:
            global popUp
            self.close()
            popUp = create_new_account._CreateAccount()
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.show()
            pass
        except Exception as error:
            print(error)
#[NON_SLOT_INDEX, SIGN_IN_SUCCESS, parsing[RSLT][TKEN], '']
#[NON_SLOT_INDEX, SIGN_IN_FAIL,  parsing[CODE], parsing[DESC]]
    def sign_in_bt_hook(self):
        global popUp
        try:
            user = self.email.text()
            psw =  self.password.text()
            if user != '' and psw != '':
                main_paras.queueForCom.put([SIGN_IN, user, psw])

                response=main_paras.api_result_que.getTimeout(10)
                if response == None:
                    popUp = wrong_password._WrongPassword()
                    popUp.setMessage(self.tr("Check network."))
                elif response[1] == SIGN_IN_FAIL:
                    popUp = wrong_password._WrongPassword()
                elif response[1] == SIGN_IN_SUCCESS:
                    main_paras.sign_in_token = response[2]
                    main_paras.sign_in_user = user
                    self.close()
                    popUp = test_info._TestInfo()

                x,y = getMainTopLeft()
                popUp.move(x,y)
                popUp.show()
                
           
        except Exception as error:
            print(error)
    def forgot_psw_hook(self):
        try:
            global popUp
            self.close()
            popUp = forgot_password._ForgotPassword()
            x,y = getMainTopLeft()
            popUp.move(x,y)
            #popUp.exec()
            #popUp.setModal(True)
            popUp.show()
            
        except Exception as error:
            print(error)
    def closeEvent(self,event):
        print("_SignIn is closing")
        

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
##    trans=QTranslator()
##    trans.load("setting_wrap.qm")
    
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    
    app = QtWidgets.QApplication(sys.argv)
##    app.installTranslator(trans)

    QtWidgets.QMainWindow
    window=_SignIn()
    
    window.show()
    print('sub window shown')
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
