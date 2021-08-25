import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
import pathlib
import queue
import time
import subprocess

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

sys.path.insert(0, parentdir)
sys.path.insert(0, currentdir)

from MyToolButton import MyToolButton
from MyStackedWidget import MyStackedWidget
import title_rc
from profile_folder.profile_wrap import _ProfileDialog
from help_folder.help_wrap import  _HelpDialog
from setting_folder.setting_wrap import _SettingDialog
from wifi_folder.wifi_list import _WifiList
from volume.volume import _Volume
from define import *
from main_paras import setMainTopLeft, getMainTopLeft, mainChannelStart, setDetectionMode, getDetectionMode, setTestMode, getTestMode, queueForGui
from wrong_password import _WrongPassword
from vkeyboard import handleVisibleChanged
try:
    from on_off.mainboard_pio import fanTurnOn
except Exception as e:
    print(e)
currentPath=pathlib.Path(__file__).parent.absolute()




class EmitThread(QtCore.QThread):
    signal= QtCore.pyqtSignal(object)
    def __init__(self, sharedQue):
        QtCore.QThread.__init__(self)
        self.qForGui=sharedQue
    def run(self):
        print("Start emit thread")
        while True:
            try:
                qItem=self.qForGui.get()
                print('in gui', qItem)
                self.signal.emit(qItem)
                self.qForGui.task_done()
            except Exception as e:
                 print(e)
        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,parent=None, qForGui=None):
        super(MainWindow, self).__init__(parent)
        emitThread = EmitThread(qForGui)
        emitThread.signal.connect(self.emitHook)
        emitThread.start()
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        loadUi(os.path.join(currentPath,'spotii.ui'),self)
        self.tempPolling = QtCore.QTimer()
        self.tempPolling.timeout.connect(self.tempMonitor)
        self.page=0
        self.slots = []
        self.allIcons = []
        self.config()
        self.show()
        
        
    def tempMonitor(self):
        try:
            result=subprocess.check_output(['vcgencmd','measure_temp']).decode("utf-8")
            tmp=int(float(result.split('=')[1].split('\'')[0]))
            #print(tmp)
            if tmp > TEMP_ON_VALUE:
                fanTurnOn(True)
            elif tmp < TEMP_OFF_VALUE:
                fanTurnOn(False)
                
        except Exception as error:
            print(error)
        
        
    def config(self):
        try:
            slot_no = 0
            self.slots = self.findChildren(QtWidgets.QStackedWidget)
            for each in self.slots:
                each.setCurrentIndex(0)
                each.setSlotNo(slot_no)
                slot_no+=1
#                self.slots.append(Ui_Slot(slot))
                #self.slots.append(slot)

            
            self.allIcons = self.title.findChildren(QtWidgets.QToolButton)
            for icon in self.allIcons:
                icon.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

            
            self.test_mode.clicked.connect(self.test_mode_hook)

            #self.help.clicked.connect(self.helpHookForTest)
            
            mainChannelStart(self.mainChannelHook)
            self.chip_mode.setText(getDetectionMode())
            QtCore.QTimer.singleShot(0, self.setupAferUi)
            
            self.tempPolling.start(10000)
        except Exception as error:
            print(error)
        
##    def config(self):
##        try:
##            slot_index = 1
##            totalSlots = self.findChildren(QtWidgets.QStackedWidget)
##            for slot in totalSlots:
##                for page in range(1,6):
##                    #print (page)
##                    slot.setCurrentIndex(page)
##                    style = '.QWidget{background-image:url(:/slot_' +str(slot_index)+ '/png/slot/slot_' +str(slot_index)+ '/' +pngName[page]+str(slot_index)+ '.png);border:0px}'
##                    #print(style)
##                    slot.currentWidget().setStyleSheet(style)
##                slot.setCurrentIndex(0)
##                slot_index+=1
##                self.slots.append(Ui_Slot(slot))
##
##            self.allIcons = self.title.findChildren(QtWidgets.QToolButton)
##            for icon in self.allIcons:
##                icon.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
##
##            
##            self.test_mode.clicked.connect(self.test_mode_hook)
##
##            self.help.clicked.connect(self.helpHookForTest)
##            
##            mainChannelStart(self.mainChannelHook)
##            self.chip_mode.setText(getDetectionMode())
##            #QtCore.QTimer.singleShot(0, self.setupAferUi)
##        except Exception as error:
##            print(error)

    def test_mode_hook(self):
        try:
            if self.test_mode.isChecked():
                self.test_mode.setText(self.tr('Normal'))
                setTestMode(TEST_MODE_NORMAL)
            else:
                self.test_mode.setText(self.tr(' Speed'))
                setTestMode(TEST_MODE_SPEED)
        except Exception as e:
            print(e)

    def mainChannelHook(self,item):
        try:
            print('main Channel', item)
            if   item == MAIN_PARA_CASSETTE_TYPE_CHIP:
                self.chip_mode.setText(CASSETTE_DETECTION_MODE_AUTO)
                setDetectionMode(CASSETTE_DETECTION_MODE_AUTO)
                for each in self.slots:
                    each.setStatus(SLOT_STATUS_EMPTY, '')
            elif item == MAIN_PARA_CASSETTE_TYPE_QR:
                self.chip_mode.setText(CASSETTE_DETECTION_MODE_MANUAL)
                setDetectionMode(CASSETTE_DETECTION_MODE_MANUAL)
                for each in self.slots:
                    each.setStatus(SLOT_STATUS_SCAN, '')
        except Exception as e:
            print(e)

    def quitHook(self):
        print('will quit')
        #QtWidgets.qApp.quit()
        self.close()


    def setupAferUi(self):
        try:
            x = self.geometry().x()
            y = self.geometry().y()
            print('main x, y', x, y)
            setMainTopLeft(x, y)

            main_x, main_y =getMainTopLeft()
            self.help.setup(_HelpDialog, main_x, main_y)
            self.wifi.setup(_WifiList, main_x+225, main_y-7)
            self.volume.setup(_Volume, main_x+275, main_y-7)
            self.setting.setup(_SettingDialog, main_x+325, main_y-7)
            self.profile_icon.setup(_ProfileDialog, main_x+357, main_y-7)

            
        except Exception as e:
            print(e)
        
    def helpHookForTest(self):
        try:
            print('help test')

            self.page= (self.page+1) %self.slots[0].totalPage()
            for index in range(0,5):                
                self.slots[index].setStatus(self.page,'La0456789')
        except Exception as e:
            print(e)

    
    def emitHook(self,item):
        try:
            print(time.strftime('%Y%m%d%H%M%S'),"emitHook:",item)
            slotNo  = item[0]
            errCode = item[1]
            qrCode  = item[2]
            
            if slotNo == SIGN_IN_FIRST_INDEX:
                global popUp
                popUp = _WrongPassword()
                popUp.setMessage(self.tr("Sign In first."),self.tr('Ok'))
                x,y = getMainTopLeft()
                popUp.move(x,y)
                popUp.show()
                
            elif slotNo == NON_SLOT_INDEX:
                for i in range(TOTAL_SLOTS):
                    self.slots[i].setStatus(SLOT_STATUS_WARNING, 'CR Error')
            elif errCode == DEVICE_STATE_TAKING_PHOTO:
                self.slots[item[0]].detecting_(qrCode)
                
            elif errCode == DEVICE_STATE_MANUAL_SCAN:
                self.slots[item[0]].setStatus(SLOT_STATUS_SCAN, qrCode)
            elif errCode == DEVICE_STATE_MANUAL_FLIP:
                self.slots[item[0]].setStatus(SLOT_STATUS_FLIP, qrCode)
            elif errCode == DEVICE_STATE_MANUAL_INVALID_QR:
                self.slots[item[0]].setStatus(SLOT_STATUS_INVALID_QR, qrCode)
            elif errCode == Positive_test_result:
                self.slots[item[0]].setStatus(SLOT_STATUS_POSITIVE, qrCode)
            elif errCode == Negative_test_result:
                self.slots[item[0]].setStatus(SLOT_STATUS_NEGATIVE, qrCode)
            elif errCode == Invalid_image_identifier:
                self.slots[item[0]].setStatus(SLOT_STATUS_INVALID, qrCode)
            elif errCode == DEVICE_STATE_CASSETTE_EMPTY:
                self.slots[item[0]].setStatus(SLOT_STATUS_EMPTY, qrCode)
            else:
                self.slots[item[0]].setStatus(SLOT_STATUS_WARNING, qrCode)
        except Exception as e:
            print(e)
        
    def closeEvent(self,event):
        print("Main window is closing")

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys

    print(QtWidgets.qApp)
#     if(QtWidgets.qApp.focusWindow().isModal()):
#         pass
#            qGuiApp->focusWindow()->setModality(Qt::WindowModal);
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    
##    trans=QTranslator()
##    trans.load("gui.qm")
    
    #qForGui=queue.Queue()
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)
##    app.installTranslator(trans)
    
    window=MainWindow(qForGui = queueForGui)
    rtn= app.exec_()
    print('main app return', rtn)
    window.close()
    sys.exit(rtn)
