from time import time
from datetime import datetime, timedelta
from xml.parsers.expat import ExpatError
from ..tools import sleep
from .project import Project


class Activity:
    SplashActivity = 'com.ss.android.ugc.aweme.lite/com.ss.android.ugc.aweme.splash.SplashActivity'  # 抖音极速版程序入口
    ExcitingVideoActivity = 'com.ss.android.ugc.aweme.lite/com.ss.android.excitingvideo.ExcitingVideoActivity'


class Text:
    iKnow = '我知道了'  # 儿童/青少年模式提醒


class ResourceID:
    av0 = 'com.ss.android.ugc.aweme.lite:id/av0'  # 关闭（12个红包 超多现金福利）
    bai = 'com.ss.android.ugc.aweme.lite:id/bai'  # 关闭（邀请5个好友必赚136元/恭喜你被红包砸中）
    bc1 = 'com.ss.android.ugc.aweme.lite:id/bc1'  # 开红包（恭喜你被红包砸中）
    e0p = 'com.ss.android.ugc.aweme.lite:id/e0p'  # 暂时不要（发现通讯录好友）
    c1m = 'com.ss.android.ugc.aweme.lite:id/c1m'  # 开宝箱（财富界面）


class Bounds:
    WatchAdsToEarnGoldCoins = '[206,1201][874,1316]'


class DYJSB(Project):
    def __init__(self, deviceSN):
        super(DYJSB, self).__init__(deviceSN)
        self.startDay = datetime.now().day

    def enterWealthInterface(self):
        self.reopenApp()
        self.uIAIns.tap([556, 1836])
        sleep(20)
        self.uIAIns.getCurrentUIHierarchy()
        print('已进入财富界面')
        self.uIAIns.click(contentDesc='立即签到')
        if self.uIAIns.click(bounds=Bounds.WatchAdsToEarnGoldCoins):
            self.afterEnterAdsInterface()
        if self.uIAIns.click(ResourceID.c1m):
            self.afterEnterAdsInterface()

    def afterEnterAdsInterface(self):
        sleep(60)
        self.adbIns.pressBackKey()
        self.uIAIns.click(contentDesc='再看一个获取')  # ExcitingVideoActivity
        sleep(60)
        self.adbIns.pressBackKey()

    def openApp(self):
        super(DYJSB, self).openApp(Activity.SplashActivity)
        sleep(20)
        try:
            if self.uIAIns.click(text=Text.iKnow):
                sleep(3)
                self.uIAIns.xml = ''
            if self.uIAIns.click(ResourceID.av0, xml=self.uIAIns.xml):
                self.uIAIns.xml = ''
            self.uIAIns.click(ResourceID.e0p, xml=self.uIAIns.xml)
        except FileNotFoundError as e:
            print(e)

    def randomSwipe(self, initRestTime=False):
        super(DYJSB, self).randomSwipe(530, 560, 530, 560, 1160, 1190, 360, 390, initRestTime)

    def watchVideo(self):
        if datetime.now().hour == 0 and datetime.now().day == self.startDay:
            self.freeMemory()
            self.adbIns.pressPowerKey()
            self.startDay = (datetime.now() + timedelta(days=1)).day
            return
        try:
            self.uIAIns.click(ResourceID.bc1)
            self.uIAIns.click(ResourceID.bai, xml=self.uIAIns.xml)
        except (FileNotFoundError, ExpatError) as e:
            print(e)
        if self.reopenAppPerHour():
            self.adbIns.keepOnline()
        # if Activity.SplashActivity not in self.adbIns.getCurrentFocus():
        #     self.reopenApp()
        self.restTime = self.restTime + self.lastTime - time()
        self.lastTime = time()
        self.randomSwipe()

    def mainloop(self):
        if not self.adbIns.device.SN == '003001001':
            return
        while True:
            if datetime.now().day == self.startDay:
                self.watchVideo()
            else:
                break
            # print('现在是', datetime.now(), '，已运行：', datetime.now() - cls.startTime,
            #       sep='', end='\n\n')
