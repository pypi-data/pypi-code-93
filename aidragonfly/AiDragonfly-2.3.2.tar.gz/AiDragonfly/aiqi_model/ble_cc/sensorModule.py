#! /usr/bin/env python
# -*- coding: utf-8 -*-

# from AiDragonfly import df
# from AiDragonfly import constantModule
# import asyncio

# import asyncio
# from . import df
# from . import constantModule

import asyncio
import AiDragonfly.aiqi_main as df
import AiDragonfly.aiqi_model.ble_cc.constantModule as constantModule


class _sensor_manage(object): #传感器管理类
    def __init__(self):
        self.color = 0
        self.sensorID = 0
        self.cnt = 0
        self.index = 0
        self.regedit_num = 0

    def set_sensor(self,sensor_class, subclass, data1, data2, data3, *, ID=1): #向传感器发送控制数据
        protocol = [0x55, 0x02, 0x06, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
        self.cnt = 0
        self.index = 0
        self.sensorID = 0
        for self.cnt in list(range(df._regeditNum)): #从注册列表中查找是否存在此传感器
            self.index = self.index + 1
            if sensor_class == df._regedit[self.cnt][5]: #传感器类型匹配
                self.sensorID = self.sensorID + 1
                if self.sensorID < ID:
                    continue
                elif self.sensorID == ID: #找到指定的传感器后,填写协议内容
                    protocol[5] = df._regedit[self.cnt][4]
                    protocol[6] = subclass
                    protocol[7] = data1
                    protocol[8] = data2
                    protocol[9] = data3
                    xor = df._data_xor_check(protocol[0:-1])
                    protocol[-2] = xor
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(df.sendDate(protocol, df.ONEBOT)) #发送
                    break

    def get_sensor_data(self,sensor_class, subclass, *, ID=1): #获取传感器数据
        protocol = [0x55, 0x02, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
        self.cnt = 0
        self.index = 0
        self.sensorID = 0
        self.regedit_num = 0
        for self.cnt in list(range(df._regeditNum)): #在注册表中查找是否有次传感器
            self.index = self.index + 1
            if sensor_class == df._regedit[self.cnt][5]:
                self.sensorID = self.sensorID + 1
                if self.sensorID < ID:
                    continue
                elif self.sensorID == ID:
                    self.regedit_num = df._regedit[self.cnt][4]
                    protocol[4] = self.regedit_num
                    protocol[5] = subclass
                    xor = df._data_xor_check(protocol[0:-1])
                    protocol[-2] = xor
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(df.sendDate(protocol, df.ONEBOT))
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(df.receiveData(df.ONEBOT))
                    break


_sensor = _sensor_manage()


class Optical(object): #多功能颜色传感器
    def __init__(self):
        self._color = 0
        self._grayScale = 0
        self._R = 0
        self._G = 0
        self._B = 0
        self._ambientLightIntensity = 0
        self._keyStatus = 0
        self._signalStrength = 0

    def get_color(self,*,ID=1): #获取颜色
        _sensor.get_sensor_data(constantModule.SENSOR_OPTICAL, constantModule.OPTICAL_COLOR, ID=ID)
        if self._color == 1:
            self._color = 'blue'
        elif self._color == 2:
            self._color = 'red'
        elif self._color == 3:
            self._color = 'yellow'
        elif self._color == 4:
            self._color = 'white'
        elif self._color == 5:
            self._color = 'green'
        elif self._color == 6:
            self._color = 'black'
        elif self._color == 8:
            self._color = 'grey'
        elif self._color == 12:
            self._color = 'purple'
        else:
            self._color = 'none'
        return self._color


    def get_grayScale(self,*,ID=1): #获取灰度值
        _sensor.get_sensor_data(constantModule.SENSOR_OPTICAL, constantModule.OPTICAL_GRAY_SCALE, ID=ID)
        return self._grayScale

    def get_RGB(self,*,ID=1): #获取RGB值
        _sensor.get_sensor_data(constantModule.SENSOR_OPTICAL, constantModule.OPTICAL_RGB, ID=ID)
        return  self._R,self._G,self._B

    def get_ambientLightIntensity(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_OPTICAL, constantModule.OPTICAL_AMBIENT_LIGHT_INTENSITY, ID=ID)
        return self._ambientLightIntensity

    def get_keyStatus(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_OPTICAL, constantModule.OPTICAL_KEY_STATUS, ID=ID)
        if self._keyStatus == 0:
            self._keyStatus = 'release'
        elif self._keyStatus == 1:
            self._keyStatus = 'press'
        return self._keyStatus

    # def get_signalStrength(self,*,ID=1):
    #     _sensor.get_sensor_data(constantModule.SENSOR_OPTICAL,constantModule.OPTICAL_SIGNAL_STRENGTH,ID=ID)
    #     return self._signalStrength

    def set_lightUp(self,R,G,B,*,ID=1):
        if R > 255 or R < 0:
            print('Data Range Error')
            print('R:[0 ~ 255]')
            print('G:[0 ~ 255]')
            print('B:[0 ~ 255]')
            return
        if G > 255 or G < 0:
            print('Data Range Error')
            print('R:[0 ~ 255]')
            print('G:[0 ~ 255]')
            print('B:[0 ~ 255]')
            return
        if B > 255 or B < 0:
            print('Data Range Error')
            print('R:[0 ~ 255]')
            print('G:[0 ~ 255]')
            print('B:[0 ~ 255]')
            return
        _sensor.set_sensor(constantModule.SENSOR_OPTICAL, constantModule.OPTICAL_LIGHT_UP, R, G, B, ID=ID)


sensor_optical = Optical()


class Laser(object): #激光传感器
    def __init__(self):
        self._distance_mm = 0
        self._distance_cm = 0
        self._keyStatus = 0
        self._signalStrength = 0

    def get_distance_mm(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_LASER, constantModule.LASER_DISTANCE_MM, ID=ID)
        return self._distance_mm

    def get_distance_cm(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_LASER, constantModule.LASER_DISTANCE_CM, ID=ID)
        return self._distance_cm

    def get_keyStatus(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_LASER, constantModule.LASER_KEY_STATUS, ID=ID)
        if self._keyStatus == 0:
            self._keyStatus = 'release'
        elif self._keyStatus == 1:
            self._keyStatus = 'press'
        return self._keyStatus

    # def get_signalStrength(self,*,ID=1):
    #     _sensor.get_sensor_data(constantModule.SENSOR_LASER,constantModule.LASER_SIGNAL_STRENGTH,ID=ID)
    #     return self._signalStrength


sensor_laser = Laser()


# class InfraredRadar(object):
#     def __init__(self):
#         self._flameDirection = 0
#         self._flameIntensity = 0
#         self._keyStatus = 0
#         self._footballDirection = 0
#
#     def get_flameDirection(self,*,ID=1):
#         _sensor.get_sensor_data(constantModule.SENSOR_FLAME,constantModule.FLAME_DIRECTION,ID=ID)
#         if self._flameDirection == 1:
#             self._flameDirection = 'second from the left'
#         elif self._flameDirection == 2:
#             self._flameDirection = 'first from the left'
#         elif self._flameDirection == 3:
#             self._flameDirection = 'middle'
#         elif self._flameDirection == 4:
#             self._flameDirection = 'first from the right'
#         elif self._flameDirection == 5:
#             self._flameDirection = 'second from the right'
#         else:
#             self._flameDirection = 'none'
#         return self._flameDirection
#
#     def get_flameIntensity(self,*,ID=1):
#         _sensor.get_sensor_data(constantModule.SENSOR_FLAME,constantModule.FLAME_INTENSITY,ID=ID)
#         return self._flameIntensity
#
#     def get_keyStatus(self,*,ID=1):
#         _sensor.get_sensor_data(constantModule.SENSOR_FLAME,constantModule.FLAME_KEY_STATUS,ID=ID)
#         if self._keyStatus == 0:
#             self._keyStatus = 'release'
#         elif self._keyStatus == 1:
#             self._keyStatus = 'press'
#         return self._keyStatus
#
#     def get_footballDirection(self,*,ID=1):
#         _sensor.get_sensor_data(constantModule.SENSOR_FLAME,constantModule.FLAME_FOOTBALL_DIRECTION,ID=ID)
#         if self._footballDirection == 1:
#             self._footballDirection = 'second from the left'
#         elif self._footballDirection == 2:
#             self._footballDirection = 'first from the left'
#         elif self._footballDirection == 3:
#             self._footballDirection = 'middle'
#         elif self._footballDirection == 4:
#             self._footballDirection = 'first from the right'
#         elif self._footballDirection == 5:
#             self._footballDirection = 'second from the right'
#         else:
#             self._footballDirection = 'none'
#         return self._footballDirection
#
#
# sensor_infraredRadar = InfraredRadar()


class Geomagnetic(object): #地磁传感器
    def __init__(self):
        self._magneticFieldAngle = 0
        self._keyStatus = 0

    def get_magneticFieldAngle(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_GEOMAGNETIC, constantModule.GEOMAGNETIC_FIELD_ANGLE, ID=ID)
        return self._magneticFieldAngle

    def get_keyStatus(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_GEOMAGNETIC, constantModule.GEOMAGNETIC_KEY_STATUS, ID=ID)
        if self._keyStatus == 0:
            self._keyStatus = 'release'
        elif self._keyStatus == 1:
            self._keyStatus = 'press'
        return self._keyStatus


sensor_geomagnetic = Geomagnetic()


class Attitude(object): #六轴传感器
    def __init__(self):
        self._dice = 0
        self._keyStatus = 0
        self._acceleration_X = 0
        self._acceleration_Y = 0
        self._acceleration_Z = 0
        self._angularVelocity_X = 0
        self._angularVelocity_Y = 0
        self._angularVelocity_Z = 0
        self._inclinationAngle_X = 0
        self._inclinationAngle_Y = 0
        self._inclinationAngle_Z = 0
        self._attitude_inclinationAngle_Z = 0
        self._steps = 0
        self._signalStrength = 0

    def get_surface(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE, constantModule.ATTITUDE_DICE, ID=ID)
        return self._dice

    def get_keyStatus(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE, constantModule.ATTITUDE_KEY_STATUS, ID=ID)
        if self._keyStatus == 0:
            self._keyStatus = 'release'
        elif self._keyStatus == 1:
            self._keyStatus = 'press'
        return self._keyStatus

    def get_acceleration_X(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE, constantModule.ATTITUDE_ACCELERATION_X, ID=ID)
        return self._acceleration_X

    def get_acceleration_Y(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE, constantModule.ATTITUDE_ACCELERATION_Y, ID=ID)
        return self._acceleration_Y

    def get_acceleration_Z(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE, constantModule.ATTITUDE_ACCELERATION_Z, ID=ID)
        return self._acceleration_Z

    def get_angularVelocity_X(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE, constantModule.ATTITUDE_ANGULAR_VELOCITY_X, ID=ID)
        return self._angularVelocity_X

    def get_angularVelocity_Y(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE, constantModule.ATTITUDE_ANGULAR_VELOCITY_Y, ID=ID)
        return self._angularVelocity_Y

    def get_angularVelocity_Z(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE, constantModule.ATTITUDE_ANGULAR_VELOCITY_Z, ID=ID)
        return self._angularVelocity_Z

    # def get_inclinationAngle_X(self,*,ID=1):
    #     _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE,constantModule.ATTITUDE_INCLINATION_ANGLE_X,ID=ID)
    #     return self._inclinationAngle_X
    #
    # def get_inclinationAngle_Y(self,*,ID=1):
    #     _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE,constantModule.ATTITUDE_INCLINATION_ANGLE_Y,ID=ID)
    #     return self._inclinationAngle_Y
    #
    # def get_inclinationAngle_Z(self,*,ID=1):
    #     _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE,constantModule.ATTITUDE_INCLINATION_ANGLE_Z,ID=ID)
    #     return self._inclinationAngle_Z
    #
    # def get_Steps(self,*,ID=1):
    #     _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE,constantModule.ATTITUDE_STEPS,ID=ID)
    #     return self._steps

    # def get_signalStrength(self,*,ID=1):
    #     _sensor.get_sensor_data(constantModule.SENSOR_ATTITUDE,constantModule.ATTITUDE_SIGNAL_STRENGTH,ID=ID)
    #     return self._signalStrength


sensor_attitude = Attitude()


class Photosensitive(object): #开发板 光敏控制函数
    def __init__(self):
        self._ambientLightIntensity = 0

    def get_photosensitiveValue(self,*,ID=1):
        _sensor.get_sensor_data(constantModule.SENSOR_PHOTOSENSITIVE,
                                constantModule.PHOTOSENSITIVE_AMBIENT_LIGHT_INTENSITY, ID=ID)
        return self._ambientLightIntensity


sensor_photosensitive = Photosensitive()


class RGBLight(object): #开发板 RGB灯控制函数
    def set_color(self,R,G,B,*,ID=1):
        if R > 255 or R < 0:
            print('Data Range Error')
            print('R:[0 ~ 255]')
            print('G:[0 ~ 255]')
            print('B:[0 ~ 255]')
            return
        if G > 255 or G < 0:
            print('Data Range Error')
            print('R:[0 ~ 255]')
            print('G:[0 ~ 255]')
            print('B:[0 ~ 255]')
            return
        if B > 255 or B < 0:
            print('Data Range Error')
            print('R:[0 ~ 255]')
            print('G:[0 ~ 255]')
            print('B:[0 ~ 255]')
            return
        _sensor.set_sensor(constantModule.SENSOR_RGBLIGHT, constantModule.RGBLIGHT_CONTROL, R, G, B, ID=ID)


sensor_RGBLight = RGBLight()


class Buzzer(object): #开发板蜂鸣器控制函数
    def set_audio(self,buzzer_tone,buzzer_note,*,ID=1):
        if buzzer_tone > 3 or buzzer_tone < 0:
            print('Data Range Error')
            print('BUZZER_TONE_HIGH、BUZZER_TONE_MIDDLE、BUZZER_TONE_LOW')
            return
        if buzzer_note > 7 or buzzer_note < 1:
            print('Data Range Error')
            print('BUZZER_NOTE_DO、BUZZER_NOTE_RE、BUZZER_NOTE_MI、BUZZER_NOTE_FA、BUZZER_NOTE_SO、BUZZER_NOTE_LA、BUZZER_NOTE_SI')
        data = buzzer_tone*10 + buzzer_note
        _sensor.set_sensor(constantModule.SENSOR_BUZZER, constantModule.BUZZER_VOLUME, 0, data, 0, ID=ID)

    def set_music(self,music,*,ID=1):
        _sensor.set_sensor(constantModule.SENSOR_BUZZER, constantModule.BUZZER_MUSIC, 0, 0, music, ID=ID)


sensor_buzzer = Buzzer()


def find_sensor(sensor, *, ID=1): #查找传感器 当多个传感器时 可以使用此函数确认对应关系
    _protocol = [0x55, 0x02, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
    _sensorID = 0
    _cnt = 0
    _index = 0
    _regedit_num = 0
    _optical_cnt = 0
    _laser_cnt = 0
    _servo_cnt = 0
    _geomagnetic_cnt = 0
    _flame_cnt = 0
    _attitude_cnt = 0
    _rgblight_cnt = 0
    _buzzer_cnt = 0
    _sensitive_cnt = 0
    _stsensor = ''

    print('\033[1;31m The list of sensors is as follows: \033[0m')
    print("+" + "-" * 11 + "+" + "-" * 15 + "+")
    print("|" + " " * 2 + "Sensor" + " " * 3 + "|" + " " + "Serial number" + " " + "|")
    print("+" + "-" * 11 + "+" + "-" * 15 + "+")
    for _cnt in list(range(df._regeditNum)): #把注册表中的传感器打印出来
        if df._regedit[_cnt][5] == constantModule.SENSOR_OPTICAL: #多功能颜色传感器
            _optical_cnt = _optical_cnt + 1
            print("|" + " " * 2 + "OPTICAL" + " " * 2 + "|" + " " * 6, _optical_cnt, " " * 6 + "|")
            print("+" + "-" * 11 + "+" + "-" * 15 + "+")
            if sensor == constantModule.SENSOR_OPTICAL:
                _stsensor = 'OPTICAL'
        elif df._regedit[_cnt][5] == constantModule.SENSOR_DIGITAL_SERVO:
            _servo_cnt = _servo_cnt + 1
            print("|" + " " * 2 + "SERVO" + " " * 4 + "|" + " " * 6, _servo_cnt, " " * 6 + "|")
            print("+" + "-" * 11 + "+" + "-" * 15 + "+")
            if sensor == constantModule.SENSOR_DIGITAL_SERVO:
                _stsensor = 'SERVO'
        elif df._regedit[_cnt][5] == constantModule.SENSOR_LASER:
            _laser_cnt = _laser_cnt + 1
            print("|" + " " * 2 + "LASER" + " " * 4 + "|" + " " * 6, _laser_cnt, " " * 6 + "|")
            print("+" + "-" * 11 + "+" + "-" * 15 + "+")
            if sensor == constantModule.SENSOR_LASER:
                _stsensor = 'LASER'
        elif df._regedit[_cnt][5] == constantModule.SENSOR_GEOMAGNETIC:
            _geomagnetic_cnt = _geomagnetic_cnt + 1
            print("|" + "GEOMAGNETIC" + "|" + " " * 6, _geomagnetic_cnt, " " * 6 + "|")
            print("+" + "-" * 11 + "+" + "-" * 15 + "+")
            if sensor == constantModule.SENSOR_GEOMAGNETIC:
                _stsensor = 'GEOMAGNETIC'
        # elif df._regedit[_cnt][5] == constantModule.SENSOR_FLAME:
        #     _flame_cnt = _flame_cnt + 1
        #     print("|" + " " * 2 + "FLAME" + " " + "|" + " " * 6, _flame_cnt, " " * 6 + "|")
        #     print("+" + "-" * 11 + "+" + "-" * 15 + "+")
        #     if sensor == constantModule.SENSOR_FLAME:
        #         _stsensor = 'FLAME'
        elif df._regedit[_cnt][5] == constantModule.SENSOR_ATTITUDE:
            _attitude_cnt = _attitude_cnt + 1
            print("|" + " " * 2 + "ATTITUDE" + " " + "|" + " " * 6, _attitude_cnt, " " * 6 + "|")
            print("+" + "-" * 11 + "+" + "-" * 15 + "+")
            if sensor == constantModule.SENSOR_ATTITUDE:
                _stsensor = 'ATTITUDE'
        elif df._regedit[_cnt][5] == constantModule.SENSOR_RGBLIGHT:
            _rgblight_cnt = _rgblight_cnt + 1
            print("|" + " " * 2 + "RGBLIGHT" + " " + "|" + " " * 6, _rgblight_cnt, " " * 6 + "|")
            print("+" + "-" * 11 + "+" + "-" * 15 + "+")
            if sensor == constantModule.SENSOR_RGBLIGHT:
                _stsensor = 'RGBLIGHT'
        elif df._regedit[_cnt][5] == constantModule.SENSOR_BUZZER:
            _buzzer_cnt = _buzzer_cnt + 1
            print("|" + " " * 2 + "BUZZER" + " " + "|" + " " * 6, _buzzer_cnt, " " * 6 + "|")
            print("+" + "-" * 11 + "+" + "-" * 15 + "+")
            if sensor == constantModule.SENSOR_BUZZER:
                _stsensor = 'BUZZER'
        elif df._regedit[_cnt][5] == constantModule.SENSOR_PHOTOSENSITIVE:
            _sensitive_cnt = _sensitive_cnt + 1
            print("|" + " " * 2 + "SENSITIVE" + " " + "|" + " " * 6, _sensitive_cnt, " " * 6 + "|")
            print("+" + "-" * 11 + "+" + "-" * 15 + "+")
            if sensor == constantModule.SENSOR_PHOTOSENSITIVE:
                _stsensor = 'SENSITIVE'

    print("Looking for the ", ID, " " * 2, _stsensor, '......')

    _sensorID = 0
    _cnt = 0
    _index = 0
    _regedit_num = 0
    for _cnt in list(range(df._regeditNum)):
        _index = _index + 1
        if sensor == df._regedit[_cnt][5]:
            _sensorID = _sensorID + 1
            if _sensorID < ID:
                continue
            elif _sensorID == ID:
                _regedit_num = df._regedit[_cnt][4]
                _protocol[4] = _regedit_num
                _protocol[5] = 0
                _protocol[7] = 1
                xor = df._data_xor_check(_protocol[0:-1])
                _protocol[-2] = xor
                loop = asyncio.get_event_loop()
                loop.run_until_complete(df.sendDate(_protocol, df.ONEBOT))
                # df._ONEBOT.receiveData()
                # df._protocol_analysis()
                break


