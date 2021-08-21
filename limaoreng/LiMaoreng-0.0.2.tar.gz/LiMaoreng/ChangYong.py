

"""常用功能
①将数字转换为年月日时分秒格式。
②使系统发出指定次数、指定音量（整十）的提示音。
"""


def shijian(t):  # 输入秒
    l1 = ['秒', '分钟', '小时', '天', '月', '年']
    l2 = [1, 60, 60, 24, 30, 365]  # 1是用来占位置来满足下面的range(1, xxx)的。
    time_ = '{:.0f}'.format(t % 60) + l1[0]
    for i in range(1, len(l1)):
        t=t//l2[i]
        if t != 0:
            time_ = '{:.0f}'.format(t % 60) + l1[i] + time_
        else:
            break
    return time_


def ding(n, loud):  # 发出’登登登‘的声音。输入次数、音量（整十）。
    import time
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    ''''''
    L = {0: -65.25, 10: -33.24, 20: -23.65, 30: -17.82, 40: -13.62, 50: -10.33,
         60: -7.63, 70: -5.33, 80: -3.34, 90: -1.58, 100: 0.0}
    """被Pycharm提示的原因是应避免使用字符’l、O、I‘来作为变量名，因为这些字符容易使人与数字1，0混淆。"""
    ''''''
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    '''被Pycharm提示了，但是我实力不够，无法消除提示，凑合用吧。'''
    ''''''
    vl = volume.GetMasterVolumeLevel()  # 获取当前音量值，0.0代表最大，-65.25代表最小。
    # vr = volume.GetVolumeRange()  # 获取音量范围，我的电脑经测试是(-65.25, 0.0, 0.03125)，第一个代表最小值，第二个代表最大值。
    ''''''
    volume.SetMasterVolumeLevel(L[loud], None)  # 改变音量, 比如-13.6代表音量是40，0.0代表音量是100。
    for i in range(n):
        print('\a', end='')
        time.sleep(1.5)
    ''''''
    volume.SetMasterVolumeLevel(vl, None)  # 恢复原音量。
