# encoding: utf-8
import os
import time
import logging
import inspect
from datetime import datetime
from robot.api.deco import keyword
import uiautomator2 as U2

dir_file = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')

class CKMobile(object):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = 0.1

    def __init__(self):
        logging.basicConfig()
        logging.getLogger().setLevel(logging.INFO)
        logger = logging.getLogger(__name__)

    def _logDebug(self, funcName, status):
        time_s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('[{}]{}: {}'.format(time_s, funcName, status))

    def _status(self, status='fail'):
        if status == 'pass':
            status = 'PASSED'
        else:
            status = 'FAILED'
        return status

    @keyword('Android Connect')
    def connect(self, deviceName=''):
        """
        Example
        | Android Connect |              |
        | Android Install | 124555323235 |
        | Android Install | android-9    |
        """
        global d
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            if (deviceName == ''):
                d = U2.connect()
                xml = d.dump_hierarchy()
                d.implicitly_wait(10)
                status = self._status('pass')
                self._logDebug(funcName, status)
            else:
                d = U2.connect(deviceName)
                xml = d.dump_hierarchy()
                d.implicitly_wait(10)
                status = self._status('pass')
                self._logDebug(funcName, status)
        except KeyboardInterrupt:
            status = self._status()
            self._logDebug(funcName, status)

    @keyword('Android Install')
    def install(self, apk):
        """
        Example
        | Android Install | app.apk                    |
        | Android Install | http://domain.com/app.apk  |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            d.app_install(apk)
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Start Application')
    def startApp(self, packageName, activityName):
        """
        Example
        | Android Start Application | .MainActivity        |
        | Android Start Application | .MainPckageActivity  |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            d.app_start(packageName, activityName)
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)


    @keyword('Android Current App')
    def currentApp(self):
        """
        Example
        | ${Retunr} | Android Current App | //*[@id="Example"]      |
        | ${Retunr} | Android Current App | //*[@name="Example"]    |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            appName = d.current_app()
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
            return appName['package']
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Click xPath')
    def xpathClick(self, xPath):
        """
        Example
        | Android Click xPath | //*[@id="Example"]    |
        | Android Click xPath | //*[@name="Example"]  |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            d.xpath(xPath).click()
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Click Element')
    def elementClick(self, attribute, value):
        """
        Example
        | Android Click Element | id          | Example |
        | Android Click Element | resourceid  | Example |
        | Android Click Element | text        | Example |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            if 'text' in attribute:
                d(textContains=value).click()
                d.implicitly_wait(10)
            elif 'resourceid' or 'id' in attribute:
                d(resourceId=value).click()
                d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Double Click xPath')
    def xpathDoubleClick(self, xPath):
        """
        Example
        | Android Double Click xPath | //*[@id="Example"]    |
        | Android Double Click xPath | //*[@name="Example"]  |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            d.xpath(xPath).double_click()
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Double Click Element')
    def elementDoubleClick(self, attribute, value):
        """
        Example
        | Android Double Click Element | id          | Example |
        | Android Double Click Element | resourceid  | Example |
        | Android Double Click Element | text        | Example |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            if 'text' in attribute:
                d(textContains=value).double_click()
                d.implicitly_wait(10)
            elif 'resourceid' or 'id' in attribute:
                d(resourceId=value).double_click()
                d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Home')
    def home(self):
        """
        Example
        | Android Home |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            appName = d.current_app()
            d.app_stop(appName['package'])
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Back')
    def back(self):
        """
        Example
        | Android Back |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            d.press("back")
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Text Input')
    def textInput(self, attribute, element, text):
        """
        Example
        | Android Text Input | id          | Example | Test    |
        | Android Text Input | resourceid  | Example | Test    |
        | Android Text Input | text        | Example | Test    |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            if 'text' in attribute:
                d(textContains=element).click()
            elif 'resourceid' or 'id' in attribute:
                d(resourceId=element).click()
            d.implicitly_wait(10)
            d.send_keys(text)
            d.press("back")
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android xPath Input')
    def xpathInput(self, xPath, text):
        """
        Example
        | Android xPath Input | //*[@id="Example"]    | Test    |
        | Android xPath Input | //*[@name="Example"]  | Example |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            d.xpath(element).click()
            d.implicitly_wait(10)
            d.send_keys(text)
            d.press("back")
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Get Text')
    def getText(self, attribute, value):
        """
        Example
        | Android Get Text | id          | Example    |
        | Android Get Text | resourceid  | id/Example |
        | Android Get Text | text        | Example    |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            if 'resourceid' or 'id' in attribute:
                text = d(resourceId=value).get_text()
                d.implicitly_wait(10)
            elif 'text' in attribute:
                text = d(textContains=value).get_text()
                d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
            return text
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Get Text by xPath')
    def getTextxPath(self, xPath):
        """
        Example
        | Android Get Text | //*[@id="Example"]     |
        | Android Get Text |  //*[@name="Example"]  |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            text = d.xpath(xPath).get_text()
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
            return text
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Screenshot')
    def screenshot(self, dir_path=''):
        """
        Example
        | Android Screenshot |          |
        | Android Screenshot | D:/test  |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            now = datetime.now()
            time = now.strftime("%Y%m%dT%H%M%S")
            if dir_path=='':
                file_screen = 'Screenshot-{}.png'.format(time)
            else:
                file_screen = '{}/Screenshot-{}.png'.format(dir_path,time)
            d.screenshot(file_screen)
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Swipe To Value')
    def swipeToValue(self, element):
        """
        Example
        | Android Swipe To Value | Example    |
        | Android Swipe To Value | Test       |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            d(scrollable=True).scroll.to(textContains=element)
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Swipe To Element')
    def swipeToElement(self, attribute, value):
        """
        Example
        | Android Swipe To Element | id         | Example    |
        | Android Swipe To Element | resourceid | id/Example |
        | Android Swipe To Element | desc       | Example    |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            if 'resourceid' or 'id' in attribute:
                d(scrollable=True).drag_to(resourceId=value)
            elif 'desc' in attribute:
                d(scrollable=True).drag_to(descriptionContains=value)
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Unlock PIN')
    def unlockPIN(self, pin_no, enter='OK'):
        """
        Example
        | Android Unlock PIN  | 112233  |        |
        | Android Unlock PIN  | 112233  | ok     |
        | Android Unlock PIN  | 112233  | enter  |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            d.unlock()
            for pin in list(pin_no):
                d(textContains=pin).click()
            d(textContains=enter).click(timeout=10)
            d.implicitly_wait(10)
            appName = d.current_app()
            d.app_stop(appName['package'])
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Notification')
    def notification(self):
        """
        Example
        | Android Notification  |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            d.open_notification()
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Skip Popups')
    def skipPopups(self, skip=True):
        """
        Example
        | Android Skip Popups  |        |
        | Android Skip Popups  | True   |
        | Android Skip Popups  | False  |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            if skip==True:
                d.disable_popups()
                d.implicitly_wait(10)
            else:
                d.disable_popups(False)
                d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Turn Screen')
    def screenTurn(self, turn=True):
        """
        Example
        | Android Turn Screen  |        |
        | Android Turn Screen  | True   |
        | Android Turn Screen  | False  |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            if turn == True:
                d.screen_on()
                d.implicitly_wait(10)
            else:
                d.screen_off()
                d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)

    @keyword('Android Key Events')
    def keyEvents(self, key):
        """
        These key names are currently supported:
        | home                 |
        | back                 |
        | left                 |
        | right                |
        | up                   |
        | down                 |
        | center               |
        | menu                 |
        | search               |
        | enter                |
        | delete               |
        | volume_up            |
        | volume_down          |
        | volume_mute          |
        | camera               |
        | power                |
        """
        status = self._status()
        funcName = inspect.stack()[0][3]
        try:
            d.press(key)
            d.implicitly_wait(10)
            status = self._status('pass')
            self._logDebug(funcName, status)
        except KeyboardInterrupt:
            self._logDebug(funcName, status)