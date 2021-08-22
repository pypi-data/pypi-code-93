from datetime import datetime, timedelta
from time import time
from xml.parsers.expat import ExpatError
from ...tools import sleep
from ...mysql import RetrieveKSJSB, UpdateKSJSB
from ...multi import runThreadsWithArgsList, runThreadsWithFunctions
from ..project import Project
from . import resourceID, activity, bounds


class KSJSB(Project):
    def __init__(self, deviceSN):
        super(KSJSB, self).__init__(deviceSN)
        self.startDay = datetime.now().day
        self.dbr = RetrieveKSJSB(deviceSN)
        self.currentFocus = ''

    def openTreasureBox(self):
        # 60*5, 60*9, 1200
        self.enterWealthInterface()
        if self.uIAIns.click(text='开宝箱得金币', xml=self.uIAIns.xml):
            if self.uIAIns.click(text='看精彩视频赚更多'):
                sleep(50)
                self.adbIns.pressBackKey()
            self.uIAIns.xml = ''

    def watchLive(self):
        self.enterWealthInterface()
        self.randomSwipe(True)
        while True:
            try:
                while self.uIAIns.getCP(text='观看精彩直播得110金币') == (0, 0):
                    self.randomSwipe(True)
                if not self.uIAIns.getDict(text='看直播领1100金币', xml=self.uIAIns.xml):
                    self.watchLive()
                    return
                if self.uIAIns.click(text='观看精彩直播得110金币', xml=self.uIAIns.xml):
                    sleep(20)
                    if activity.PhotoDetailActivity not in self.adbIns.getCurrentFocus():
                        self.watchLive()
                        return
                    sleep(89)
                    self.exitLive()
                else:
                    break
            except FileNotFoundError as e:
                print(e)
                self.watchLive()

    def exitLive(self):
        self.adbIns.pressBackKey()
        if activity.PhotoDetailActivity not in self.adbIns.getCurrentFocus():
            return
        try:
            if self.uIAIns.click(resourceID.live_exit_button):
                self.uIAIns.xml = ''
            self.uIAIns.click(resourceID.exit_btn, xml=self.uIAIns.xml)
        except FileNotFoundError as e:
            print(e)
            self.exitLive()
        if activity.PhotoDetailActivity in self.adbIns.getCurrentFocus():
            self.exitLive()

    def viewAds(self):
        self.enterWealthInterface()
        self.randomSwipe(True)
        while True:
            try:
                if activity.KwaiYodaWebViewActivity not in self.adbIns.getCurrentFocus():
                    self.viewAds()
                    return
                elif self.uIAIns.click(text='观看广告单日最高可得5000金币') or self.uIAIns.click(
                        text='每次100金币，每天1000金币', xml=self.uIAIns.xml):
                    sleep(50)
                    self.adbIns.pressBackKey()
                else:
                    break
            except FileNotFoundError as e:
                print(e)
                self.viewAds()

    def signIn(self):
        self.enterWealthInterface()
        if not self.uIAIns.getDict(text='今天签到可领'):
            return
        try:
            while self.uIAIns.getCP(text='今天签到可领') == (0, 0):
                self.randomSwipe(True)
            self.uIAIns.click(text='今天签到可领')
            self.afterSignIn()
        except FileNotFoundError as e:
            print(e)
            self.signIn()

    def afterSignIn(self):
        if self.uIAIns.click('', '打开签到提醒'):  # 需要授权
            self.uIAIns.xml = ''
        elif self.uIAIns.click('', '看广告再得', xml=self.uIAIns.xml):
            sleep(60)
            self.adbIns.pressBackKey()
            self.uIAIns.xml = ''
        if self.uIAIns.click(bounds=bounds.closeInviteFriendsToMakeMoney, xml=self.uIAIns.xml):
            self.uIAIns.xml = ''

    def enterWealthInterface(self, reopen=True):
        if reopen:
            self.reopenApp()
        try:
            if not self.uIAIns.click(resourceID.red_packet_anim, xml=self.uIAIns.xml
                                     ) and activity.MiniAppActivity0 in self.adbIns.getCurrentFocus():
                self.randomSwipe(True)
                self.enterWealthInterface(False)
                return
            sleep(13)
            self.uIAIns.getCurrentUIHierarchy()
            print('已进入财富界面')
            if self.uIAIns.click('', '立即领取今日现金'):
                self.uIAIns.xml = ''
                self.enterWealthInterface()
                return
            if self.uIAIns.click('', '立即签到', xml=self.uIAIns.xml):
                self.uIAIns.xml = ''
                self.afterSignIn()
            # if self.uIAIns.click(bounds=bounds.closeInviteFriendsToMakeMoney, xml=self.uIAIns.xml):
            #     self.uIAIns.xml = ''
            if self.uIAIns.click(bounds=bounds.closeCongratulations, xml=self.uIAIns.xml):
                self.uIAIns.xml = ''
        except FileNotFoundError as e:
            print(e)
            self.enterWealthInterface(False)

    @classmethod
    def updateWealthWithMulti(cls, devicesSN):
        runThreadsWithArgsList(cls.initIns, devicesSN)
        functions = []
        for i in cls.instances:
            functions.append(i.updateWealth)
        runThreadsWithFunctions(functions)

    def enterMyWealthInterface(self, reopen=True):
        self.enterWealthInterface(reopen)
        self.uIAIns.click(text='可用抵用金（张）')
        sleep(9)

    def updateWealth(self, reopen=True):
        self.enterMyWealthInterface(reopen)
        try:
            goldCoins, cashCoupons = self.getWealth()
            if not goldCoins == self.dbr.goldCoins:
                UpdateKSJSB(self.adbIns.device.SN).updateGoldCoins(goldCoins)
            if not cashCoupons == self.dbr.cashCoupons:
                UpdateKSJSB(self.adbIns.device.SN).updateCashCoupons(cashCoupons)
        except FileNotFoundError as e:
            print(e)
            self.updateWealth(False)

    def getWealth(self):
        dics = self.uIAIns.getDicts(bounds='[-1,351][-1,459]')
        # print(dics)
        goldCoins = dics[0]['@text']
        if 'w' in goldCoins:
            goldCoins = 10000 * float(goldCoins[:-1])
        cashCoupons = float(dics[1]['@text'])
        # print(goldCoins, cashCoupons)
        return goldCoins, cashCoupons

    def openApp(self, reopen=True):
        if reopen:
            super(KSJSB, self).openApp(activity.HomeActivity)
            sleep(16)
        try:
            if self.uIAIns.click(resourceID.close):
                self.uIAIns.xml = ''
            if self.uIAIns.click(resourceID.iv_close_common_dialog, xml=self.uIAIns.xml):
                self.uIAIns.xml = ''
            if self.uIAIns.click(resourceID.positive, xml=self.uIAIns.xml):
                self.uIAIns.xml = ''
            if self.uIAIns.click(resourceID.tv_upgrade_now, xml=self.uIAIns.xml):
                self.uIAIns.xml = ''
                self.adbIns.pressBackKey()
            while not self.uIAIns.getDict(resourceID.red_packet_anim, xml=self.uIAIns.xml):
                self.randomSwipe(True)
                self.uIAIns.xml = ''
        except FileNotFoundError as e:
            print(e)
            self.randomSwipe(True)
            sleep(6)
            self.openApp(False)

    def initSleepTime(self):
        print('restTime=%s' % self.restTime)
        if self.restTime <= 0:
            return
        elif self.uIAIns.getDict(resourceID.live_simple_play_swipe_text, xml=self.uIAIns.xml):
            pass
        elif self.uIAIns.getDict(resourceID.open_long_atlas, xml=self.uIAIns.xml):
            pass
        else:
            return
        self.restTime = 0

    def watchVideo(self):
        if self.reopenAppPerHour(False):
            self.adbIns.keepOnline()
            self.openTreasureBox()
            self.reopenApp()
        try:
            if datetime.now().hour > 5 and self.uIAIns.getDict(resourceID.red_packet_anim):
                if not self.uIAIns.getDict(resourceID.cycle_progress, xml=self.uIAIns.xml):
                    self.viewAds()
                    self.watchLive()
                    self.openTreasureBox()
                    self.signIn()
                    self.updateWealth()
                    self.freeMemory()
                    self.adbIns.pressPowerKey()
                    self.startDay = (datetime.now() + timedelta(days=1)).day
                    return
            if activity.PhotoDetailActivity in self.adbIns.getCurrentFocus():
                self.exitLive()
                self.randomSwipe(True)
            self.uIAIns.click(resourceID.button2, xml=self.uIAIns.xml)
            self.initSleepTime()
        except (FileNotFoundError, ExpatError) as e:
            print(e)
            self.randomSwipe(True)
        self.restTime = self.restTime + self.lastTime - time()
        self.lastTime = time()
        self.randomSwipe()
        self.uIAIns.xml = ''

    def randomSwipe(self, initRestTime=False):
        super(KSJSB, self).randomSwipe(360, 390, 360, 390, 1160, 1190, 260, 290, initRestTime)

    def mainloop(self):
        while True:
            if datetime.now().day == self.startDay:
                self.watchVideo()
            else:
                self.openTreasureBox()
                break
