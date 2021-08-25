#! /usr/bin/env python
# -*- coding: utf-8 -*-
import atexit
import threading

import AiDragonfly
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from AiDragonfly.aiqi_model.bluetooth import aiqi_bluetooth
from AiDragonfly.comm_protocol.aiqi_blue_report import bluereport
from AiDragonfly.comm_protocol.aiqi_mesh_report import mesh_report, _mesh_login_class
from AiDragonfly.common.onebot_common_function import Aiqi_Print_HEX
from AiDragonfly.aiqi_model.ble_cc import constantModule, motorModule, musicModule, sensorModule
import asyncio
import time
import sys

# import aiqi_model

# The global variable
import AiDragonfly.aiqi_bluetooth_device_type as aiqi_blue_type
from AiDragonfly.Get_Mesh_Devices_Message import Get_Onebot_Device_Message_Init
import AiDragonfly.aiqi_bluetooth_save_json as aiqi_file

_volume = 0
_engine = 0
_voltage = 0
_regeditNum = 0
_regedit = [[0 for i in range(100)] for j in range(25)]
__dev_type = 0

blue_scan_parm = None
onebot_client = None

mesh_control_flag = 0
mesh_mode_flag = 0

mesh_config_ack = False


__onebot_login = _mesh_login_class()
__aiqi_adapter = aiqi_bluetooth.Aiqi_Bluetooth_Class()


def _protocol_analysis(num, data):  # 数据接收分析函数，根据报文协议 解析收到的数据
    global _regeditNum, _regedit, _volume, _engine, _voltage
    global i, __onebot_login
    global mesh_config_ack
    global mesh_control_flag, mesh_mode_flag
    length = num
    _receive_message = data
    # Aiqi_Print_HEX(data)
    if length > 3:  # 接收到的数据个数 小于三个 则抛弃
        if _receive_message[0] == 0x55:  # 红蓝主控的报文分析 0x55是红蓝主控协议的报头
            buf = _receive_message
            if buf[0] == 0x55 and buf[-1] == 0xAA:  # 协议报头 报尾
                if buf[1] == 0x01 and buf[2] == 0x04 and buf[3] == 0x01 and buf[4] == 0x00:  # 根据具体协议解析即可
                    _volume = buf[5]
                    _engine = buf[6]
                    # print('音量',buf)
                elif buf[1] == 0x02 and buf[2] == 0x06 and buf[3] == 0x00 and buf[4] == 0xC8:
                    volume = buf[8] * 256 + buf[9]
                    # print('Synchronous voltage')
                    # print('主控电压',buf)
                    pass
                elif buf[1] == 0x01 and buf[2] == 0x02 and buf[3] == 0x00 and buf[4] == 0x00:
                    # print('The heartbeat packets')
                    pass
                elif buf[1] == 0x01 and buf[2] == 0x03 and buf[3] == 0x00 and buf[4] == 0x01:
                    # print('The registry starts uploading')
                    pass
                elif buf[1] == 0x01 and buf[2] == 0x03 and buf[3] == 0x01 and buf[4] == 0x01:
                    # print('Registry upload complete')
                    pass
                elif buf[1] == 0x01 and buf[2] == 0x07 and buf[3] == 0x00:
                    # print('SN',buf)
                    pass
                elif buf[1] == 0x01 and buf[2] == 0x06 and buf[3] == 0x00:
                    musicModule._version = (
                                                   buf[4] << 24) + (buf[5] << 16) + (buf[6] << 8) + buf[7]
                    # print('固件版本号',buf)
                elif buf[1] == 0x01 and buf[2] == 0x06 and buf[3] == 0x01:
                    # print('语音版本号',buf)
                    pass
                elif buf[1] == 0x05 and buf[2] == 0x00 and buf[3] == 0x00:  # 注册信息处理
                    if _regeditNum == 0:  # 注册个数为零 存储第一条注册信息
                        # print('有新传感器,类型：', buf[5],'。  注册号：',buf[4],'已注册个数：',_regeditNum+1)
                        # print('数据：',buf)
                        _regedit[_regeditNum][0:20] = buf[0:20]
                        _regeditNum = _regeditNum + 1
                    else:
                        while True:
                            # 接收到注册报文后，先判断注册表中是否已存在此注册信息
                            for i in list(range(_regeditNum)):
                                tmp1 = buf[6:11]
                                tmp2 = bytearray(_regedit[i][6:11])
                                if tmp1 == tmp2:
                                    break
                                else:
                                    i = i + 1
                            if i == _regeditNum:  # 注册表中没有此条注册信息，填入注册表
                                # print('有新传感器,类型：', buf[5],'。  注册号：',buf[4],'已注册个数：',_regeditNum+1)
                                # print('数据：',buf)
                                _regedit[_regeditNum][0:20] = buf[0:20]
                                _regeditNum = _regeditNum + 1
                                break
                            else:
                                break
                # 以上主要为主控连接成功后的 初始交互信息和注册表
                # 下面主要是接收到传感器数据的处理
                elif buf[1] == 0x02 and buf[2] == 0x02 and buf[3] == 0x05:
                    motorModule.motor._rotation_completed_flag = 1
                    motorModule.motor._rotation_completed_port = buf[4]
                elif buf[1] == 0x02 and buf[2] == 0x06 and buf[3] == 0x00 and buf[4] == 0x0B:
                    if buf[11] == 4 or buf[11] == 5 or buf[11] == 6 or buf[11] == 7:
                        motorModule.motor._port_speed = buf[5] * 256 + buf[6]
                    elif buf[11] == 0 or buf[11] == 1 or buf[11] == 2 or buf[11] == 3:
                        motorModule.motor._port_angle = buf[5] * 256 + buf[6]

                elif buf[1] == 0x02 and buf[2] == 0x06 and buf[3] == 0x00:
                    if buf[10] == 0x00:  # 传感器状态在线
                        if buf[4] == sensorModule._sensor.regedit_num:  # 首先判断传感器注册号是否匹配
                            for i in list(range(_regeditNum)):
                                # 注册号匹配
                                if sensorModule._sensor.regedit_num == _regedit[i][4]:
                                    if _regedit[i][5] == constantModule.SENSOR_DIGITAL_SERVO:  # 舵机
                                        if buf[11] == constantModule.DIGITALSERVO_GETANGLE:
                                            motorModule.digitalServo._angle = buf[5] * \
                                                                              256 + buf[6]

                                    # 设备类型匹配,处理数据.这个是多功能颜色传感器
                                    elif _regedit[i][5] == constantModule.SENSOR_OPTICAL:
                                        if buf[11] == constantModule.OPTICAL_COLOR:  # 颜色
                                            sensorModule.sensor_optical._color = buf[6]
                                        elif buf[11] == constantModule.OPTICAL_GRAY_SCALE:  # 灰度
                                            sensorModule.sensor_optical._grayScale = buf[6]
                                        elif buf[11] == constantModule.OPTICAL_RGB:  # RGB
                                            sensorModule.sensor_optical._R = buf[5]
                                            sensorModule.sensor_optical._G = buf[6]
                                            sensorModule.sensor_optical._B = buf[7]
                                        # 环境光
                                        elif buf[11] == constantModule.OPTICAL_AMBIENT_LIGHT_INTENSITY:
                                            sensorModule.sensor_optical._ambientLightIntensity = buf[
                                                                                                     5] * 256 + buf[6]
                                        elif buf[11] == constantModule.OPTICAL_KEY_STATUS:
                                            sensorModule.sensor_optical._keyStatus = buf[6]
                                        # elif buf[11] == constantModule.OPTICAL_SIGNAL_STRENGTH:
                                        #     sensorModule.sensor_optical._signalStrength = buf[6]

                                    # 光敏传感器
                                    elif _regedit[i][5] == constantModule.SENSOR_PHOTOSENSITIVE:
                                        if buf[11] == constantModule.PHOTOSENSITIVE_AMBIENT_LIGHT_INTENSITY:
                                            sensorModule.sensor_photosensitive._ambientLightIntensity = buf[5] * 256 + \
                                                                                                        buf[6]

                                    elif _regedit[i][5] == constantModule.SENSOR_LASER:  # 激光传感器
                                        if buf[11] == constantModule.LASER_DISTANCE_MM:
                                            sensorModule.sensor_laser._distance_mm = buf[5] * \
                                                                                     256 + buf[6]
                                        elif buf[11] == constantModule.LASER_DISTANCE_CM:
                                            sensorModule.sensor_laser._distance_cm = buf[6]
                                        elif buf[11] == constantModule.LASER_KEY_STATUS:
                                            sensorModule.sensor_laser._keyStatus = buf[6]
                                        # elif buf[11] == constantModule.LASER_SIGNAL_STRENGTH:
                                        #     sensorModule.sensor_laser._signal_strength = buf[6]

                                    # elif _regedit[i][5] == constantModule.SENSOR_FLAME:
                                    #     if buf[11] == constantModule.FLAME_DIRECTION:
                                    #         sensorModule.sensor_infraredRadar._flameDirection = buf[6]
                                    #     elif buf[11] == constantModule.FLAME_INTENSITY:
                                    #         sensorModule.sensor_infraredRadar._flameIntensity = buf[6]
                                    #     elif buf[11] == constantModule.FLAME_KEY_STATUS:
                                    #         sensorModule.sensor_infraredRadar._keyStatus = buf[6]
                                    #     elif buf[11] == constantModule.FLAME_FOOTBALL_DIRECTION:
                                    #         sensorModule.sensor_infraredRadar._footballDirection = buf[6]

                                    elif _regedit[i][5] == constantModule.SENSOR_GEOMAGNETIC:  # 地磁传感器
                                        if buf[11] == constantModule.GEOMAGNETIC_FIELD_ANGLE:
                                            sensorModule.sensor_geomagnetic._magneticFieldAngle = buf[
                                                                                                      5] * 256 + buf[6]
                                        elif buf[11] == constantModule.GEOMAGNETIC_KEY_STATUS:
                                            sensorModule.sensor_geomagnetic._keyStatus = buf[6]

                                    elif _regedit[i][5] == constantModule.SENSOR_ATTITUDE:  # 六轴传感器
                                        if buf[11] == constantModule.ATTITUDE_DICE:
                                            sensorModule.sensor_attitude._dice = buf[6]
                                        # elif buf[11] == constantModule.ATTITUDE_STEPS:
                                        #     sensorModule.sensor_attitude._steps = buf[5]*256 + buf[6]
                                        # elif buf[11] == constantModule.ATTITUDE_SIGNAL_STRENGTH:
                                        #     sensorModule.sensor_attitude._signalStrength = buf[6]
                                        elif buf[11] == constantModule.ATTITUDE_KEY_STATUS:
                                            sensorModule.sensor_attitude._keyStatus = buf[6]
                                        elif buf[11] == constantModule.ATTITUDE_ACCELERATION_X:
                                            sensorModule.sensor_attitude._acceleration_X = buf[
                                                                                               5] * 256 + buf[6]
                                        elif buf[11] == constantModule.ATTITUDE_ACCELERATION_Y:
                                            sensorModule.sensor_attitude._acceleration_Y = buf[
                                                                                               5] * 256 + buf[6]
                                        elif buf[11] == constantModule.ATTITUDE_ACCELERATION_Z:
                                            sensorModule.sensor_attitude._acceleration_Z = buf[
                                                                                               5] * 256 + buf[6]
                                        elif buf[11] == constantModule.ATTITUDE_ANGULAR_VELOCITY_X:
                                            sensorModule.sensor_attitude._angularVelocity_X = buf[
                                                                                                  5] * 256 + buf[6]
                                        elif buf[11] == constantModule.ATTITUDE_ANGULAR_VELOCITY_Y:
                                            sensorModule.sensor_attitude._angularVelocity_Y = buf[
                                                                                                  5] * 256 + buf[6]
                                        elif buf[11] == constantModule.ATTITUDE_ANGULAR_VELOCITY_Z:
                                            sensorModule.sensor_attitude._angularVelocity_Z = buf[
                                                                                                  5] * 256 + buf[6]
                                        # elif buf[11] == constantModule.ATTITUDE_INCLINATION_ANGLE_X:
                                        #     sensorModule.sensor_attitude._inclinationAngle_X = buf[6]
                                        # elif buf[11] == constantModule.ATTITUDE_INCLINATION_ANGLE_Y:
                                        #     sensorModule.sensor_attitude._inclinationAngle_Y = buf[6]
                                        # elif buf[11] == constantModule.ATTITUDE_INCLINATION_ANGLE_Z:
                                        #     sensorModule.sensor_attitude._inclinationAngle_Z = buf[6]

                                    else:
                                        print('Sensor not found')
                    else:
                        print('sensor offline')
        elif _receive_message[0] == 0x01:  # mesh设备的处理报文
            buf = _receive_message
            if buf[1] == 0x79:  # 配置回应
                if buf[2] == 0:
                    mesh_config_ack = True
                elif buf[2] == 1:
                    mesh_config_ack = False
                else:
                    mesh_config_ack = False
            elif buf[1] == 0x53:  # 接收到随机值
                mesh_random = buf[2]
                __onebot_login.dev_random = buf[2]

                mesh_sn_flag = 0
            elif buf[1] == 0x47:  # 成功登录
                if buf[2] == 1:
                    __onebot_login.dev_login_stats = True
                else:
                    __onebot_login.dev_login_stats = False
            elif buf[1] == 0x81:  # 平衡机器人模式
                if buf[2] == 0:
                    mesh_mode_flag = 0
                elif buf[2] == 1:
                    mesh_mode_flag = 1
                elif buf[3] == 2:
                    mesh_mode_flag = 2
                elif buf[4] == 3:
                    mesh_mode_flag = 3

        elif _receive_message[0] == 0x04:  # mesh设备的处理报文  接收到版本号
            buf = _receive_message
            if buf[1] == 0x4C:
                v1 = buf[2] << 24
                v2 = buf[3] << 16
                v3 = buf[4] << 8
                v4 = buf[5]
                mesh_version = v1 + v2 + v3 + v4
                # print('version ' + str(mesh_version))
                __onebot_login.dev_version = mesh_version

        elif _receive_message[0] == 0x07:  # mesh设备的处理报文 接收到SN
            buf = _receive_message
            if buf[1] == 0x4E:
                __onebot_login.dev_sn = buf[2:9]


__dev_mac_addr = ''

__onebot_local_save_list = []

__get_message_done_stats = False


def __get_mssage_callback(dev_list):
    global __get_message_done_stats, __onebot_local_save_list

    __onebot_local_save_list = []
    __onebot_local_save_list = dev_list[:]
    __get_message_done_stats = True


__bluetooth_scan_list = []
__wait_char_stats = False
__print_char = ""
__print_char_num = 0
__print_char_num_max = 0
def __print_wait_char(time=0.1,maxnum=10):
    global __print_char,__print_char_num,__wait_char_stats
    __print_char_num_max = maxnum
    if __wait_char_stats:
        __print_char +='█'
        print("\r"+__print_char+"  "+str(__print_char_num)+"/"+str(maxnum), end='')
        threading.Timer(time, __print_wait_char,args=(time,maxnum)).start()
    __print_char_num += 1
    if __print_char_num > __print_char_num_max and __print_char_num_max != 0:
        __wait_char_stats = False


def __bluetooth_scan_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    global __bluetooth_scan_list

    if device.name != '' and device.name is not None:
        if len(__bluetooth_scan_list) != 0:
            for item in __bluetooth_scan_list:
                if item.address == device.address:
                    return
        __bluetooth_scan_list.append(device)
        # print('bluetooth_scan_callback' + device.name + ' ' + device.address, "RSSI:", device.rssi)


def __user_console_select(devs):
    user_select_buff = devs[:]
    user_done = False
    devs_index = []
    user_new_buff = []
    for item in devs:
        devs_index.append(item.index)

    while not user_done:
        def checkvalid(check_buff):
            for i in check_buff:
                if i not in devs_index:
                    print(i)
                    print(devs_index)
                    return False
            return True
        aiqi_blue_type.Print_Scan_Onebot_Device(user_select_buff)
        print('Please enter a number to be connected Shown in red, multiple sequences separated by spaces,Or directly enter, all the default configuration')
        print('Input sequence, determine the control sequence, please choose according to your needs')
        user_input = input('Separated by a space：').split()
        if len(user_input) != 0:
            user_input = list(map(int,user_input))
            if checkvalid(user_input):
                user_new_buff = []
                for i in user_input:
                    for item in user_select_buff:
                        if item.index == i:
                            user_new_buff.append(item)
                user_done = True
            else:
                print("Input error, please try again")
        else:
            user_new_buff = user_select_buff[:]
            user_done = True
    return user_new_buff


__App_Reset = ''
async def onebot_getdevices_process():
    global __dev_type, __dev_mac_addr,__wait_char_stats

    global __bluetooth_scan_list, __get_message_done_stats

    local_save_list = []
    scan_stats = True
    if __App_Reset == 'new':
        aiqi_file.delete_local_save_device()
    else:
        local_save_list = aiqi_file.Read_Local_Onebot_Device()
    if len(local_save_list) == 0:
        print('No local storage device found')
    else:
        scan_stats = False
        __dev_mac_addr = local_save_list[0].devid
        __onebot_local_save_list = local_save_list[:]
        __dev_type = aiqi_blue_type.Read_Onebot_Device_type(__onebot_local_save_list)
    if scan_stats:
        print('Start scanning')
        __bluetooth_scan_list = []
        __aiqi_adapter.set_scan_callback_regiser(__bluetooth_scan_callback)
        scancnt = 40
        scan_timeout = 40
        await __aiqi_adapter.scan_ctrl(True)
        __wait_char_stats = True
        __print_wait_char(0.5,blue_scan_parm.scantimeout/0.5)

        await asyncio.sleep(blue_scan_parm.scantimeout+1)
        await __aiqi_adapter.scan_ctrl(False)
        __wait_char_stats = False
        print('\nscan stop')

        devices = __bluetooth_scan_list[:]
        devices = __aiqi_adapter.scan_devices_operation(
            devices, blue_scan_parm.scannamelist, blue_scan_parm.scanmaclist)
        __onebot_local_save_list = aiqi_blue_type.select_onebot_devices(
            devices, scan_name=blue_scan_parm.scannamelist)
        if len(devices) == 0:
            print(
                "\n" + '\033[1;31m Please Turn on the master motor power switch or Please insert the Bluetooth adapter \033[0m')
            sys.exit('aiqi quit')

        __dev_type = aiqi_blue_type.Read_Onebot_Device_type(__onebot_local_save_list)
        print('Getting information......')
        if __dev_type == aiqi_blue_type.aiqi_device_type_class.Aiqi_Onebot_Mesh_Dev:
            await Get_Onebot_Device_Message_Init(__onebot_local_save_list, __get_mssage_callback)
            while __get_message_done_stats is False:
                pass
                time.sleep(0.1)  # 等待获取完成
            __get_message_done_stats = False
            __onebot_local_save_list = __user_console_select(__onebot_local_save_list)[:]
        aiqi_file.Save_Local_Onebot_Device(__onebot_local_save_list)
        print("Successfully saved")
        # 获取设备信息
    print('The local device information is as follows:   ')
    aiqi_file.print_Local_Onebot_Device()
    time.sleep(1)  # 等待断开
    __dev_mac_addr = __onebot_local_save_list[0].devid


'''
onebot login
'''


async def __onebot_login_process():
    global __wait_char_stats
    try:
        print("Please wait for a connection, up to eight seconds......")
        __wait_char_stats = True
        __print_wait_char(0.5,30)
        await __aiqi_adapter.connect(__dev_mac_addr,timeout=8)

    except:
        __wait_char_stats = False
        print("\nDevice connection timeout")
        sys.exit("0")
    __wait_char_stats = False

    __aiqi_adapter.set_disconnect_callback_register(_disconnect_callback)
    __aiqi_adapter.set_receive_callback_register(_protocol_analysis)
    global onebot_client, ONEBOT_Connect_Stats

    if __dev_type == 1 or __dev_type == 4:  # 蓝主控
        print('shake .....')
        # 发送连接报文
        __aiqi_adapter.set_receive_callback_register(_protocol_analysis)
        await __aiqi_adapter.sendData(bluereport.create_connect)
        # await client.write_gatt_char(aiqi_uuid.Aiqi_Bluetooth_Rx_Char_Uuid, bluereport.create_connect)
        # await client.start_notify(aiqi_uuid.Aiqi_Bluetooth_Tx_Char_Uuid,
        #                           _protocol_analysis)  # 打开蓝牙设备的发送，接收数据都在_protocol_analysis函数中
        await asyncio.sleep(3)
        # await client.stop_notify(aiqi_uuid.Aiqi_Bluetooth_Tx_Char_Uuid)  # 停止蓝牙设备的发送

    elif __dev_type == 2 or __dev_type == 3:  # 红主控 or 越野车 同上
        print('shake .....')


    elif __dev_type == 5:  # mesh 设备 mesh设备连接后需要根据设备版本号判断是否加密
        print('Detection version.....', end='')
        await __aiqi_adapter.senddata(mesh_report.get_version)
        time.sleep(0.1)
        print('version ' + __onebot_login.Get_Version_Str())
        if __onebot_login.dev_version >= __onebot_login.need_login_version:
            await __aiqi_adapter.senddata(mesh_report.get_sn)
            time.sleep(0.1)
            if __onebot_login.dev_sn is not None:
                await __aiqi_adapter.senddata(mesh_report.get_random)
                await asyncio.sleep(0.05)
                time.sleep(0.1)
                mesh_report.mesh_sn = []
                mesh_report.mesh_sn = __onebot_login.dev_sn[:]
                mesh_report.mesh_random = __onebot_login.dev_random
                await __aiqi_adapter.senddata(mesh_report.login_in)
                await asyncio.sleep(0.05)
                time.sleep(0.1)
                if __onebot_login.dev_login_stats:
                    print('login ok')
                else:
                    print('login err')
                    sys.exit('login err')
            else:
                print('sn err')
                sys.exit('sn err')
        elif __onebot_login.dev_version == 0:
            print('versin err')
            sys.exit('err')
        else:
            print('free login')

    else:
        print('设备类型不存在:', __dev_type)
        sys.exit('未知的设备类型')


def Aiqi_Bluetooth_Send(data, log=False):
    if log:
        Aiqi_Print_HEX(data)
    if __onebot_login.dev_login_stats:
        data.append(__onebot_login.dev_random)
    if __aiqi_adapter.connect_stats is True:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(sendDate(data))  # 配置设备 发送模式配置信息
    else:
        print('ble is disconnect')


def __Aiqi_Bluetooth_Retry_Connect():
    print('Aiqi_Bluetooth_Retry_Connect')


# 蓝牙发送数据
async def sendDate(data):
    databytes = bytearray(data)
    if __aiqi_adapter.connect_stats:
        await __aiqi_adapter.senddata(databytes)
    else:
        print('ble disconect')



User_Disconnect_Handle = None

def _disconnect_callback(res):
    global ONEBOT_Connect_Stats, onebot_client
    # print('disconnect')
    ONEBOT_Connect_Stats = False
    onebot_client = None
    __onebot_login.Clear()
    if User_Disconnect_Handle is not None:
        User_Disconnect_Handle(res)




def Aiqi_Bluetooth_Disconnect_CallBack_Register(callback):
    global User_Disconnect_Handle
    # print('connect callback reg')
    User_Disconnect_Handle = callback


ONEBOT_Connect_Stats = False

async def app_exit():
    await __aiqi_adapter.disconnect()
    time.sleep(0.1)

@atexit.register
def atexit_fun():
    print('sys exit')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app_exit())


'''
app_reset : if is 'new' ,will clear local save all devices

'''
def start(app_reset='',scantimeout=5,rssi=-100,namelist=[],maclist=[]):
    global blue_scan_parm,__App_Reset
    __App_Reset = app_reset.lower()
    print('start')
    parm = aiqi_blue_type.aiqi_bluetooth_scan_class()
    parm.scantimeout = scantimeout
    parm.scannamelist = namelist[:]
    parm.scanmaclist = maclist[:]

    blue_scan_parm = parm
    loop = asyncio.get_event_loop()
    loop.run_until_complete(onebot_getdevices_process())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(__onebot_login_process())

    return onebot_client
