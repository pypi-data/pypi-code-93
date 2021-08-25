#! /usr/bin/env python
# -*- coding: utf-8 -*-

import AiDragonfly.aiqi_main as main

import asyncio

import time

from AiDragonfly.aiqi_bluetooth_save_json import Read_Local_Onebot_Device
from AiDragonfly.common.onebot_common_function import Aiqi_Print_HEX

mesh_super_conf_name_list = ["OneBot_XL_M", "OneBot_St_M", "OneBot_BL_M"]
mesh_super_conf_dev_list = []

__log_title = 'mesh_model '

'''
speed -100 至 100
'''


def __speed_to_xl_speed(speed):
    re_spd = 0
    spd = speed
    if spd > 100:
        spd = 100
    elif spd < -100:
        spd = -100

    if spd >= 0:
        re_spd = spd
    else:
        re_spd = 100 - spd
    if re_spd == 100:
        re_spd = 99

    return re_spd


'''
speed -100 至 100
'''


def __speed_to_bl_speed(speed):
    re_spd = 0
    spd = speed
    if spd > 100:
        spd = 100
    elif spd < -100:
        spd = -100
    re_spd = spd

    return re_spd


'''
speed -150 至 150
'''


def __speed_to_st_speed(speed):
    zero_angle = 173
    re_spd = 0
    spd = speed
    if spd > 150:
        spd = 150
    elif spd < -150:
        spd = -150
    re_spd = zero_angle + spd
    return re_spd


'''
速度buff ,如 speed_buff=[100,-100]
+100，对应xl 电机、平衡电机，速度正传100，
+100 对应舵机，左转100度
max value  100 电机
max value  150 舵机
min value -100 电机
min value -150 舵机
'''


def speed_ctrl(speed_buff):
    if len(speed_buff) == 0:
        print('please check speed_buff')
        return
    dev_len = len(mesh_super_conf_dev_list)
    dev_list = mesh_super_conf_dev_list

    tx_buf = bytearray(2+dev_len * 2)
    for i in tx_buf:
        i = 0
    tx_buf[0] = dev_len * 2
    tx_buf[1] = 122
    index = 0
    x = 0
    for spd in speed_buff:
        v1 = 0
        if dev_list[x].name == "OneBot_XL_M":
            v1 = __speed_to_xl_speed(spd)
        elif dev_list[x].name == "OneBot_BL_M":
            v1 = __speed_to_bl_speed(spd)
        elif dev_list[x].name == "OneBot_St_M":
            v1 = __speed_to_st_speed(spd)
        else:
            print('speed analy err')
            break
        tx_buf[2 + index] = v1 >> 8
        tx_buf[2 + index + 1] = v1 & 0xff
        index += 2
        x += 1
        if x > dev_len-1:
            break

    main.Aiqi_Bluetooth_Send(tx_buf)
    time.sleep(0.05)


'''
Currently only supports configuration "OneBot_XL_M","OneBot_St_M","OneBot_BL_M"
When configuring, it will automatically search and configure from the list by default, and the unsupported devices will automatically skip
Default first directly connected to the sweep

'''


def mesh_configure():
    global mesh_super_conf_dev_list
    local_dev = Read_Local_Onebot_Device()
    conf_item = []
    for localitem in local_dev:
        if localitem.name in mesh_super_conf_name_list:
            conf_item.append(localitem)
    mesh_super_conf_dev_list = conf_item[:]

    del conf_item[0]  #
    dev_len = len(conf_item)

    if dev_len == 0 or dev_len > 6:
        # print('dev num is ' + str(dev_len) + ',不需要super配置')
        return
    tx_buf = bytearray(5 + dev_len * 2)

    tx_buf[0] = 3 + dev_len * 2

    tx_buf[1] = 121
    # Aiqi_Print_HEX(tx_buf)
    dev_mes = [0, 0, 0, 0, 0, 0]  # 配置设备类型属性
    dev_mes_index = 0
    for item in conf_item:
        if item.name == 'OneBot_XL_M' or item.name == 'OneBot_BL_M':
            dev_mes[dev_mes_index] = 1
        elif item.name == 'OneBot_St_M':
            dev_mes[dev_mes_index] = 2
        tx_buf[5 + dev_mes_index] = item.mesh_addr >> 8
        tx_buf[5 + dev_mes_index + 1] = item.mesh_addr & 0xff
        dev_mes_index += 1

    tx_buf[2] = dev_mes[0] << 4 + dev_mes[1]
    tx_buf[3] = dev_mes[2] << 4 + dev_mes[3]
    tx_buf[4] = dev_mes[4] << 4 + dev_mes[5]
    try:
        main.Aiqi_Bluetooth_Send(tx_buf)
    except:
        print(__log_title+'bluetooth send err')
    print(__log_title+'configure ok')




