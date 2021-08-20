# -*- coding: utf-8 -*-

import time
from pinpong.board import Board
from pinpong.extension.microbit import MBScreen

Board("microbit").begin()#初始化，选择板型和端口号，不输入端口号则进行自动识别
#Board("microbit","COM36").begin()   #windows下指定端口初始化
#Board("microbit","/dev/ttyACM0").begin()   #linux下指定端口初始化
#Board("microbit","/dev/cu.usbmodem14101").begin()   #mac下指定端口初始化

display = MBScreen()
#heart,heart_small,arrow_n,arrow_s,arrow_w,arrow_e,arrow_ne,arrow_nw,arrow_se,arrow_sw,yes,no
#happy,sad,angry,silly,smile,asleep,square,square_small,triangle,triangle_left,diamond_small
#music_crotchet,music_quaver,music_quavers,clock1,clock2,clock3,clock4,clock5,clock6,clock7
#clock8,clock9,clock10,clock11,clock12,skull,butterfly,chessboard,confused,cow,diamond,duck,
#fabulous,chost,giraffe,house,meh,pacman,pitchfork,rabbit,rollerskate,snake,stickfigure
#surprised,sword,tagget,tortoise,tshirt,umbrella,xmas
display.show("heart")
#显示图案
#display.scroll("hello world")
#显示字符串
#display.set_pixel(0,0)
#点亮坐标x,y的灯
#display.off_pixel(0,0)
#熄灭坐标x,y的灯
#display.set_brightness(1)
#设置灯的亮度
#display.clear()
#关闭所有点阵
while True:
    pass



