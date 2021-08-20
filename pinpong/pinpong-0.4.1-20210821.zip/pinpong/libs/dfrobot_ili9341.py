# -*- coding: utf-8 -*-
import time
from pinpong.board import gboard,SPI

class ILI9341:
  initCmd = [
    #flag cmd 最高位为1表示后2位是延时，低7位表示参数的个数
    0x01,0xCF,3,0x00,0xC1,0X30,
    0x01,0xED,4,0x64,0x03,0X12,0X81,
    0x01,0xE8,3,0x85,0x00,0x78,
    0x01,0xCB,5,0x39,0x2C,0x00,0x34,0x02,
    0x01,0xF7,1,0x20,
    0x01,0xEA,2,0x00,0x00,
    0x01,0xC0,1,0x10,
    0x01,0xC1,1,0x00,
    0x01,0xC5,2,0x30,0x30,
    0x01,0xC7,1,0xB7,
    0x01,0x3A,1,0x55,
    0x01,0x36,1,0x08,
    0x01,0xB1,2,0x00,0x1A,
    0x01,0xB6,2,0x0A ,0xA2,
    0x01,0xF2,1,0x00,
    0x01,0x26,1,0x01,
    0x01,0xE0,15,0x0F,0x2A,0x28,0x08,0x0E,0x08,0x54,0xA9,0x43,0x0A,0x0F,0x00,0x00,0x00,0x00,
    0x01,0XE1,15,0x00,0x15,0x17,0x07,0x11,0x06,0x2B,0x56,0x3C,0x05,0x10,0x0F,0x3F,0x3F,0x0F,
    0x01,0x2B,4,0x00,0x00,0x01,0x3f,
    0x01,0x2A,4,0x00,0x00,0x00,0xef,
    0x01,0x11,0x80,0,120,
    0x01,0x29, 0,
    0x00
  ]
  
  _ILI9341_COLSET = 0x2A
  _ILI9341_RAWSET = 0x2B
  _ILI9341_RAMWR  = 0x2C

  COLOR_BLACK  = 0x0000   #  黑色    
  COLOR_NAVY   = 0x000F   #  深蓝色  
  COLOR_DGREEN = 0x03E0   #  深绿色 
  
  def __init__(self, width, height):
    self.width = width
    self.height = height

  def begin(self):
    offset = 0
    while self.initCmd[offset]:
      offset += 1
      cmd = self.initCmd[offset];
      offset += 1
      val = self.initCmd[offset];
      offset += 1
      argsNum = val & 0x7F;
      if val & 0x80:
        duration = self.initCmd[offset]*255 + self.initCmd[offset+1];
        time.sleep(duration/1000);
        offset += 2;
      self.sendCommand(cmd, self.initCmd[offset:offset+argsNum])
      offset += argsNum

  def fill(self, color):
    self.sendCommand(self._ILI9341_COLSET)
    self.sendData16(0)
    self.sendData16(self.width-1)
    self.sendCommand(self._ILI9341_RAWSET)
    self.sendData16(0)
    self.sendData16(self.height-1)
    self.sendCommand(self._ILI9341_RAMWR)
    self.sendColor(color, self.width*self.height)

class ILI9341_SPI(ILI9341):
  def __init__(self, board=None, width=240, height=320, device_num=1, dc=None, res=None, cs=None):
    if board is None:
      board = gboard

    self.board = board
    self.dc=dc
    self.cs=cs
    self.res=res
    self.spi = SPI(device_num)
    super().__init__(width, height)

  def begin(self):
    if self.res:
      self.res.value(1)
    if self.dc:
      self.dc.value(1)

    if self.res:
      self.res.value(0)
      time.sleep(0.2)
      self.res.value(1)
      time.sleep(0.2)
    super().begin()

  def sendCommand(self, cmd, value=None):
    self.dc.value(0)
    self.spi.write([cmd])
    self.dc.value(1)
    if value:
      self.spi.write(value)

  def sendData16(self, data):
    self.spi.write([data>>8, data&0xff])
  
  def sendColor(self, color, len):
    buf = [color>>8, color&0xff]*len
    self.spi.write(buf)
