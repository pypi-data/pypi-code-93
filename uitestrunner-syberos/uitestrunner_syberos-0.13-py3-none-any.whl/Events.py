from time import sleep


class Events:
    device = None
    app = None
    item = None

    def __init__(self, d=None, a=None, i=None):
        self.device = d
        self.app = a
        self.item = i

    @staticmethod
    def __reply_status_check(reply):
        if reply.status == 200:
            return True
        return False

    def get_blank_timeout(self):
        return int(self.device.con.get(path="getBlankTimeout").read())

    def set_blank_timeout(self, timeout):
        return self.__reply_status_check(self.device.con.get(path="setBlankTimeout", args="sec=" + str(timeout)))

    def set_display_on(self):
        return self.__reply_status_check(self.device.con.get(path="setDisplayState", args="state=0"))

    def set_display_off(self):
        return self.__reply_status_check(self.device.con.get(path="setDisplayState", args="state=1"))

    def set_display_dim(self):
        return self.__reply_status_check(self.device.con.get(path="setDisplayState", args="state=0")) and \
               self.__reply_status_check(self.device.con.get(path="setDisplayState", args="state=2"))

    def get_display_state(self):
        reply = int(str(self.device.con.get(path="getDisplayState").read(), 'utf-8'))
        if reply == 0:
            return "on"
        elif reply == 1:
            return "off"
        elif reply == 2:
            return "dim"
        return "unknown"

    def lock(self):
        return self.__reply_status_check(self.device.con.get(path="setLockState", args="state=0"))

    def unlock(self):
        dis_state = int(str(self.device.con.get(path="getDisplayState").read(), 'utf-8'))
        if dis_state == 0 or dis_state == 2:
            return self.__reply_status_check(self.device.con.get(path="setLockState", args="state=1"))
        elif dis_state == 1:
            if self.set_display_on():
                sleep(1)
                return self.__reply_status_check(self.device.con.get(path="setLockState", args="state=1"))
        return False

    def get_lock_state(self):
        reply = int(str(self.device.con.get(path="getLockState").read(), 'utf-8'))
        if reply == 0:
            return "locked"
        elif reply == 1:
            return "unlocked"
        return "unknown"

    def submit_string(self, text):
        return self.__reply_status_check(self.device.con.get(path="sendCommitString", args="str=" + text))

    def click(self, x, y):
        return self.__reply_status_check(self.device.con.get(path="sendTouchEvent", args="points=" + str(x) + "|" + str(y)))

    def multi_click(self, points):
        args = ""
        for point in points:
            args += str(point[0]) + "|" + str(point[1])
            if points.index(point) != len(points) - 1:
                args += ","
        return self.__reply_status_check(self.device.con.get(path="sendTouchEvent", args="points=" + args))

    def slide(self, x1, y1, x2, y2):
        return self.__reply_status_check(self.device.con.get(path="sendSlideEvent", args="sliders=" + str(x1) + "|" + str(y1) + "->" + str(x2) + "|" + str(y2)))

    def multi_slide(self, points1, points2):
        args = ""
        for point1 in points1:
            args += str(point1[0]) + "|" + str(point1[1]) + "->" + str(points2[points1.index(point1)][0]) + "|" + str(points2[points1.index(point1)][1])
            if points1.index(point1) != len(points1) - 1:
                args += ","
        return self.__reply_status_check(self.device.con.get(path="sendSlideEvent", args="sliders=" + args))

    def back(self):
        return self.__reply_status_check(self.device.con.get(path="sendBackKeyEvent"))

    def home(self):
        return self.__reply_status_check(self.device.con.get(path="sendHomeKeyEvent"))

    def menu(self):
        return self.__reply_status_check(self.device.con.get(path="sendMenuKeyEvent"))

    def volume_up(self, delay=0):
        return self.__reply_status_check(self.device.con.get(path="sendVolumeUpKeyEvent", args="delay=" + str(delay)))

    def volume_down(self, delay=0):
        return self.__reply_status_check(self.device.con.get(path="sendVolumeDownKeyEvent", args="delay=" + str(delay)))

