
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#parentdir = os.path.dirname(currentdir)
#sys.path.insert(0, parentdir)
sys.path.insert(0, currentdir)
#from emit_thread import _EmitThread
#from channel import Channel
from non_block_queue import NonBlockQue
from define import *

import queue

queueForGui=queue.Queue()
queueForCom=queue.Queue()
queueForResult=queue.Queue()


TITLE_HIGH = 48
MAIN_X = 0
MAIN_Y = 0
def getMainTopLeft():
    return MAIN_X, MAIN_Y
def setMainTopLeft(x,y):
    global MAIN_X
    global MAIN_Y
    MAIN_X = x
    MAIN_Y = y + TITLE_HIGH

##from PyQt5 import QtCore
##signal = QtCore.pyqtSignal(object)
##def mainChannelStart(hook):
##    global signal
##    signal.connect(hook)
##def mainChannelNotify(item):
##    signal.emit(item)


from PyQt5 import QtCore
class _EmitThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)

main_ui_channel=_EmitThread()
def mainChannelStart(hook):
    global main_ui_channel
    main_ui_channel.signal.connect(hook)
#    main_ui_channel.start()
def mainChannelNotify(item):
    main_ui_channel.signal.emit(item)


        
keyboard_up = _EmitThread()

#     try:
#         data = some_queue.get(False)
#         # If `False`, the program is not blocked. `Queue.Empty` is thrown if
#         # the queue is empty
#     except Queue.Empty:
#         data = None

manual_command_que = NonBlockQue()
api_result_que = NonBlockQue()
type_in_que = NonBlockQue()

# toGui=Channel()
# toCom=Channel()
# forResult=Channel()
# 

manual_operation = [MANUAL_OPERATION_START,MANUAL_OPERATION_START,MANUAL_OPERATION_START,MANUAL_OPERATION_START,MANUAL_OPERATION_START]# for manual command setting sequence
def setOperation(index, operation):
    manual_operation[index] = operation
def getOperation(index):
    return manual_operation[index]

decMode = CASSETTE_DETECTION_MODE_AUTO #for different cassette identify mode base on cassette type
def setDetectionMode(mode):
    global decMode
    decMode=mode
    if decMode == CASSETTE_DETECTION_MODE_MANUAL:
        for i in range(0, TOTAL_SLOTS):
            setOperation(i, MANUAL_OPERATION_START)
def getDetectionMode():
    return decMode

test_mode = 'speed'
testMode = TEST_MODE_SPEED
def setTestMode(mode):
    global testMode
    global test_mode
    testMode=mode
    if testMode == TEST_MODE_SPEED:
        test_mode = 'speed'
    else:
        test_mode = 'normal'
        
def getTestMode():
    return testMode
sign_in_user =''
sign_in_token =''
test_place =''
test_city  =''
test_country =''
test_provider =''
report_email_1 =''
report_email_2 =''
serial=''

    
