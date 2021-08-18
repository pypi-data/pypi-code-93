# -*- coding: utf-8 -*
import time
from pinpong.board import Board
from pinpong.libs.microbit_motor import Microbit_Motor #导入Microbit_Motor库

Board("microbit").begin()  #初始化，选择板型和端口号，不输入端口号则进行自动识别
#Board("microbit","COM36").begin()  #windows下指定端口初始化
#Board("microbit","/dev/ttyACM0").begin()   #linux下指定端口初始化
#Board("microbit","/dev/cu.usbmodem14101").begin()   #mac下指定端口初始化

motorbit = Microbit_Motor()

#步进电机有M1_M2，M1_M2，CW代表正转，CCW代表反转， 50代表角度 
#motorbit.stepper_degree(motorbit.M1_M2, motorbit.CW, 50)
#步进电机有M1_M2，M1_M2，CW代表正转，CCW代表反转， 10代表圈数
motorbit.stepper_turn(motorbit.M1_M2, motorbit.CW, 10)

