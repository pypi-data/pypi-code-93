

"""为了让右边的警示消失，改了好多语法和习惯。"""


import pyautogui as p
import random as r
import time as t


def suo_ding(name, region=(0, 0, 1920, 1080), confidence=0.7):  # 锁定目标图片并捕捉（点击），区域默认全屏。当函数后有注释时，开头空两行。
    location = p.locateOnScreen(name, region=region, confidence=confidence, grayscale=True)
    # confidence像素差异、grayscale灰度，返回一个元组。
    if location:
        x1, y1, w, h = location  # 图片左上角的坐标，图片的宽、高。
        x2 = x1+w
        y2 = y1+h  # 计算得到图片右下角的坐标。
        X = r.randint(int(x1 + 0.1 * (x2 - x1)), int(x2 - 0.1 * (x2 - x1)))  # 将坐标区域向图片中心靠近，即图片边缘区域不点击。
        Y = r.randint(int(y1 + 0.1 * (y2 - y1)), int(y2 - 0.1 * (y2 - y1)))  # 获取随机位置X,Y。
        bu_zhuo(name, X, Y, region, confidence)
        return True
    else:
        return False


def bu_zhuo(name, x, y, region, confidence):
    L = ['p.easeInQuad', 'p.easeOutQuad', 'p.easeInOutQuad', 'p.easeInBounce', 'p.easeInElastic']  # 鼠标的5种移动方式。
    p.moveTo(x, y, 0.1, eval(L[r.randint(0, 4)]))  # 第3个参数，默认最小移动时间是0.1s。randint(0,4)取0到4整数。
    p.click(button='left')
    t.sleep(0.01)
    p.click(button='left')  # 防止点击无反应，补点一下。
    while True:
        t.sleep(0.1)  # 点击后，延迟一下，等待系统反应。
        if not suo_ding(name, region=region, confidence=confidence):  # 进入循环，防止点击无反应。
            break
