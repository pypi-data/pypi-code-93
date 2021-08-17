from ..tools import sleep
from .project import Project


class Activity:
    KiwiChatActivity = 'com.sh.shuihulu.kiwi/k.i.w.i.m.assemble.activity.KiwiChatActivity'
    AccessibilitySettingsActivity = 'u0 com.android.settings/com.android.settings' \
                                    '.Settings$AccessibilitySettingsActivity'
    MainActivity = 'com.sh.shuihulu.kiwi/com.yicheng.assemble.activity.MainActivity'


class ResourceID:
    iv_tippopu_close = 'com.sh.shuihulu.kiwi:id/iv_tippopu_close'  # 回复男生搭讪需先录制交友宣言和真人认证，认证后可以继续领取搭讪红包哦


class Text:
    toMakeFriendsDeclaration = '去交友宣言'


class HY(Project):
    def __init__(self, deviceSN):
        super(HY, self).__init__(deviceSN)

    def openApp(self):
        super(HY, self).openApp(Activity.MainActivity)
        sleep(6)

    def mainloop(self, reopen=False):
        self.uIAIns.tap([56, 126])
        if reopen:
            self.reopenApp()
        try:
            if self.uIAIns.click(ResourceID.iv_tippopu_close):
                self.uIAIns.xml = ''
            self.uIAIns.click(text=Text.toMakeFriendsDeclaration, xml=self.uIAIns.xml)
        except FileNotFoundError as e:
            print(e)
            self.mainloop(True)
        if 'com.sh.shuihulu.kiwi' not in self.adbIns.getCurrentFocus():
            self.mainloop(True)
        self.uIAIns.tap([56, 126])
