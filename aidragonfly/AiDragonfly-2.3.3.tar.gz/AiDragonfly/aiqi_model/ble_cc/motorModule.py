#! /usr/bin/env python
# -*- coding: utf-8 -*-

# from AiDragonfly import constantModule
# from AiDragonfly import df
# from AiDragonfly import sensorModule

# from . import constantModule
# from . import df
# from . import sensorModule
# import asyncio

import AiDragonfly.aiqi_model.ble_cc.constantModule as constantModule
import AiDragonfly.aiqi_main as df
import AiDragonfly.aiqi_model.ble_cc.sensorModule as  sensorModule
import asyncio


class Motor_manage(object): #电机管理类
    def __init__(self):
        self._port_speed = 0
        self._port_angle = 0
        self._rotation_completed_flag = 0
        self._rotation_completed_port = 0

    def _get_data(self,subclass): #获取数据
        protocol = [0x55, 0x02, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]

        protocol[4] = 0x0B
        protocol[5] = subclass
        xor = df._data_xor_check(protocol[0:-1])
        protocol[-2] = xor
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.sendDate(protocol, df.ONEBOT))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.receiveData(df.ONEBOT))

    def set_speed_portA(self,speed): #设置端口A速度
        protocol = [0x55, 0x02, 0x02, 0x00, 0x80, 0x00, 0x80, 0x00, 0x00, 0x80, 0x80
            , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
        if speed > 127 or speed < -127:
            print('Data Range Error')
            print('speed:[-127 ~ 127]')
            return
        if speed == 0:
            speed = speed + 128
        elif speed < 0:
            speed = 128 - abs(speed)
            if speed > 127:
                speed = 127
        elif speed > 0:
            speed = speed + 128
            if speed > 255:
                speed = 255
        protocol[4] = speed
        xor = df._data_xor_check(protocol[0:-1])
        protocol[-2] = xor
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.sendDate(protocol, df.ONEBOT))

    def set_speed_portB(self,speed):
        protocol = [0x55, 0x02, 0x02, 0x00, 0x80, 0x00, 0x80, 0x00, 0x00, 0x80, 0x80
            , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
        if speed > 127 or speed < -127:
            print('Data Range Error')
            print('speed:[-127 ~ 127]')
            return
        if speed == 0:
            speed = speed + 128
        elif speed < 0:
            speed = 128 - abs(speed)
            if speed > 127:
                speed = 127
        elif speed > 0:
            speed = speed + 128
            if speed > 255:
                speed = 255
        protocol[6] = speed
        xor = df._data_xor_check(protocol[0:-1])
        protocol[-2] = xor
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.sendDate(protocol, df.ONEBOT))

    def set_speed_portC(self,speed):
        protocol = [0x55, 0x02, 0x02, 0x00, 0x80, 0x00, 0x80, 0x00, 0x00, 0x80, 0x80
            , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
        if speed > 127 or speed < -127:
            print('Data Range Error')
            print('speed:[-127 ~ 127]')
            return
        if speed == 0:
            speed = speed + 128
        elif speed < 0:
            speed = 128 - abs(speed)
            if speed > 127:
                speed = 127
        elif speed > 0:
            speed = speed + 128
            if speed > 255:
                speed = 255
        protocol[9] = speed
        xor = df._data_xor_check(protocol[0:-1])
        protocol[-2] = xor
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.sendDate(protocol, df.ONEBOT))

    def set_speed_portD(self,speed):
        protocol = [0x55, 0x02, 0x02, 0x00, 0x80, 0x00, 0x80, 0x00, 0x00, 0x80, 0x80
            , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
        if speed > 127 or speed < -127:
            print('Data Range Error')
            print('speed:[-127 ~ 127]')
            return
        if speed == 0:
            speed = speed + 128
        elif speed < 0:
            speed = 128 - abs(speed)
            if speed > 127:
                speed = 127
        elif speed > 0:
            speed = speed + 128
            if speed > 255:
                speed = 255
        protocol[10] = speed
        xor = df._data_xor_check(protocol[0:-1])
        protocol[-2] = xor
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.sendDate(protocol, df.ONEBOT))

    def set_speed(self,portA_speed,portB_speed,portC_speed,portD_speed): #同时设置四个端口速度
        protocol = [0x55, 0x02, 0x02, 0x00, 0x80, 0x00, 0x80, 0x00, 0x00, 0x80, 0x80
            , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
        if portA_speed > 127 or portA_speed < -127:
            print('Data Range Error')
            print('portA_speed:[-127 ~ 127]')
            return
        if portB_speed > 127 or portB_speed < -127:
            print('Data Range Error')
            print('portB_speed:[-127 ~ 127]')
            return
        if portC_speed > 127 or portC_speed < -127:
            print('Data Range Error')
            print('portC_speed:[-127 ~ 127]')
            return
        if portD_speed > 127 or portD_speed < -127:
            print('Data Range Error')
            print('portD_speed:[-127 ~ 127]')
            return

        if portA_speed == 0:
            portA_speed = portA_speed + 128
        elif portA_speed < 0:
            portA_speed = 128 - abs(portA_speed)
            if portA_speed > 127:
                portA_speed = 127
        elif portA_speed > 0:
            portA_speed = portA_speed + 128
            if portA_speed > 255:
                portA_speed = 255

        if portB_speed == 0:
            portB_speed = portB_speed + 128
        elif portB_speed < 0:
            portB_speed = 128 - abs(portB_speed)
            if portB_speed > 127:
                portB_speed = 127
        elif portB_speed > 0:
            portB_speed = portB_speed + 128
            if portB_speed > 255:
                portB_speed = 255

        if portC_speed == 0:
            portC_speed = portC_speed + 128
        elif portC_speed < 0:
            portC_speed = 128 - abs(portC_speed)
            if portC_speed > 127:
                portC_speed = 127
        elif portC_speed > 0:
            portC_speed = portC_speed + 128
            if portC_speed > 255:
                portC_speed = 255

        if portD_speed == 0:
            portD_speed = portD_speed + 128
        elif portD_speed < 0:
            portD_speed = 128 - abs(portD_speed)
            if portD_speed > 127:
                portD_speed = 127
        elif portD_speed > 0:
            portD_speed = portD_speed + 128
            if portD_speed > 255:
                portD_speed = 255

        protocol[4] = portA_speed
        protocol[6] = portB_speed
        protocol[9] = portC_speed
        protocol[10] = portD_speed
        xor = df._data_xor_check(protocol[0:-1])
        protocol[-2] = xor
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.sendDate(protocol, df.ONEBOT))

    def set_angle(self,motor_port,speed,angle): #设置角度
        protocol = [0x55, 0x02, 0x02, 0x04, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00
            , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
        motor_port = motor_port + 1
        if motor_port > 4:
            print('Data Range Error')
            print('port:[1 ~ 4]')
            print('speed:[-127 ~ 127]')
            print('angle:[0 ~ 65535]')
            return
        if speed > 127 or speed < -127:
            print('Data Range Error')
            print('port:[1 ~ 4]')
            print('speed:[-127 ~ 127]')
            print('angle:[0 ~ 65535]')
            return
        if angle > 65535 or angle < 0:
            print('Data Range Error')
            print('port:[1 ~ 4]')
            print('speed:[-127 ~ 127]')
            print('angle:[0 ~ 65535]')
            return

        if speed == 0:
            speed = speed + 128
        elif speed < 0:
            speed = 128 - abs(speed)
            if speed > 127:
                speed = 127
        elif speed > 0:
            speed = speed + 128
            if speed > 255:
                speed = 255

        anglel = angle % 256
        angleh = angle >> 8

        protocol[4] = motor_port
        protocol[5] = speed
        protocol[6] = angleh
        protocol[7] = anglel
        xor = df._data_xor_check(protocol[0:-1])
        protocol[-2] = xor
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.sendDate(protocol, df.ONEBOT))

    def get_speed(self,motor_port): #读取电机端口速度值
        motor_port = motor_port + 4
        if motor_port > 7 or motor_port < 4:
            print('Data Range Error')
            print('speedport:[4 ~ 7]')
            return
        self._get_data(motor_port)
        return df._hex2int(self._port_speed, 16)

    def get_angle(self, motor_port): #获取端口角度
        if motor_port < 0 or motor_port > 3:
            print('Data Range Error')
            print('angleport:[0 ~ 3]')
            return
        self._get_data(motor_port)
        return df._hex2int(self._port_angle, 16)

    def whichPort_rotationCompleted(self): #判断哪个端口电机转动完成
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.receiveData(df.ONEBOT))
        if self._rotation_completed_flag:
            self._rotation_completed_flag = 0
            if self._rotation_completed_port == 0x01:
                self._rotation_completed_port = 'portA_completed'
            elif self._rotation_completed_port == 0x02:
                self._rotation_completed_port = 'portB_completed'
            elif self._rotation_completed_port == 0x03:
                self._rotation_completed_port = 'portC_completed'
            elif self._rotation_completed_port == 0x04:
                self._rotation_completed_port = 'portD_completed'

            return self._rotation_completed_port


motor = Motor_manage()


class DigitalServo_manage(object): #舵机管理类
    def __init__(self):
        self._angle = 0

    def set_angle(self,angle,*,ID=1): #设置舵机角度
        if angle > 160 or angle < -160:
            print('Data Range Error')
            print('angle:[-160 ~ 160]')
            return
        angle = df._int2hex(angle,16)
        anglel = angle % 256
        angleh = angle >> 8
        sensorModule._sensor.set_sensor(constantModule.SENSOR_DIGITAL_SERVO, constantModule.DIGITALSERVO_SETANGLE, angleh, anglel, 0, ID=ID)

    def set_power(self,power,*,ID=1): #设置舵机功率
        if power > 100 or power < -100:
            print('Data Range Error')
            print('power:[-100 ~ 100]')
            return
        power = df._int2hex(power,8)
        sensorModule._sensor.set_sensor(constantModule.SENSOR_DIGITAL_SERVO, constantModule.DIGITALSERVO_SETPOWER, 0, power, 0, ID=ID)

    def get_angle(self,*,ID=1): #获取舵机角度
        sensorModule._sensor.get_sensor_data(constantModule.SENSOR_DIGITAL_SERVO, constantModule.DIGITALSERVO_GETANGLE, ID=ID)
        return df._hex2int(self._angle,16)


digitalServo = DigitalServo_manage()



