import cv2
import numpy as np
from simple_pid import PID


def get_color_mask(bgr, lower, upper):
    """获取颜色遮罩

    Parameters
    ----------
    bgr : numpy.ndarray
        bgr格式的图像
    lower : numpy.ndarray
        颜色下界，HSV表示
    upper : numpy.ndarray
        颜色上界，HSV表示

    Returns
    -------
    numpy.ndarray
        颜色遮罩
    """

    # 利用高斯模糊减少图像噪声
    res = cv2.GaussianBlur(bgr, (5, 5), 0)

    # 将图像转为HSV格式，因为HSV可以更方便表示颜色
    res = cv2.cvtColor(res, cv2.COLOR_BGR2HSV)

    # 利用`cv2.inRange()`函数创建颜色遮罩
    res = cv2.inRange(res, lower, upper)

    return res


class ColorTracker():
    def __init__(self, lower_hsv, upper_hsv, min_r) -> None:
        self.lower_hsv = np.array(lower_hsv)
        self.upper_hsv = np.array(upper_hsv)
        self.min_r = min_r

    def find_max_color_blob(self, bgr):
        """获取颜色坐标

        Parameters
        ----------
        bgr : numpy.ndarray
            bgr 格式的图像

        Returns
        -------
        x : int
        y : int
        r : int
        """
        mask = get_color_mask(bgr, self.lower_hsv, self.upper_hsv)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
        x, y, r = -1, -1, -1
        ret = False
        if len(cnts) > 0:
            # 查找最大的轮廓
            c = max(cnts, key=cv2.contourArea)

            # 利用该轮廓计算其外接圆形
            (x, y), r = cv2.minEnclosingCircle(c)
            x, y, r = int(x), int(y), int(r)
            if r > self.min_r:
                cv2.circle(bgr, (x, y), r, (255, 0, 0), 2)  # 在BGR图像上绘制圆
                ret = True
        h, w = bgr.shape[:2]
        x /= w
        y /= h
        return ret, x, y, r

    def set_x_pid(self,
                  kp,
                  ki=0,
                  kd=0,
                  setpoint=0,
                  output_limits=(None, None)):
        self.x_pid = PID(kp,
                         ki,
                         kd,
                         setpoint=setpoint,
                         output_limits=output_limits)

    def set_y_pid(self,
                  kp,
                  ki=0,
                  kd=0,
                  setpoint=0,
                  output_limits=(None, None)):
        self.y_pid = PID(kp,
                         ki,
                         kd,
                         setpoint=setpoint,
                         output_limits=output_limits)

    def set_z_pid(self,
                  kp,
                  ki=0,
                  kd=0,
                  setpoint=0,
                  output_limits=(None, None)):
        self.z_pid = PID(kp,
                         ki,
                         kd,
                         setpoint=setpoint,
                         output_limits=output_limits)

    def get_x_output(self, detection):
        if not hasattr(self, 'x_pid') or not detection[0]:
            return 0

        error = detection[1] - 0.5
        return self.x_pid(error)

    def get_y_output(self, detection):
        if not hasattr(self, 'y_pid') or not detection[0]:
            return 0
        error = detection[2] - 0.5
        return self.y_pid(error)

    def get_z_output(self, detection):
        if not hasattr(self, 'z_pid') or not detection[0]:
            return 0
        return self.z_pid(detection[3])
