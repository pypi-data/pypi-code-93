# -*- coding: utf-8 -*-

import time
from pinpong.board import Board,Pin
from pinpong.libs.dfrobot_ili9341 import ILI9341_SPI #导入ili9341库

Board("RPi").begin()

dc = Pin(21, Pin.OUT)
res = Pin(26, Pin.OUT)

lcd = ILI9341_SPI(width=240, height=320, device_num=1, dc=dc, res=res) #初始化屏幕，传入屏幕像素点数
lcd.begin()

while True:
  lcd.fill(lcd.COLOR_BLACK)
  time.sleep(1)
  lcd.fill(lcd.COLOR_NAVY)
  time.sleep(1)
  lcd.fill(lcd.COLOR_DGREEN)
  time.sleep(1)
